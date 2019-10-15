import asyncio
import collections
import dataclasses
import functools
import logging
import time
from typing import Any, Mapping, Set

import aiofiles
import aioprocessing
import backoff
import structlog
import structlog.processors
import structlog.stdlib
from schema import Schema, And, Use, Optional
import yaml
import zmq.asyncio

from runtime import get_version
from runtime.service import SERVICES
from runtime.service.base import Service
from runtime.monitoring.retry import Proxy
from runtime.util.exception import EmergencyStopException

LOGGER = structlog.get_logger()


@dataclasses.dataclass
class ServiceSupervisor:
    subprocesses: Mapping[int, Any] = dataclasses.field(default_factory=dict)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        for subprocess in self.subprocesses.values():
            self.terminate(subprocess)

    @backoff.on_predicate(backoff.constant, interval=1, max_tries=5, logger=LOGGER)
    async def spawn(self, name: str, service: Service, *args, **kwargs):
        subprocess = aioprocessing.AioProcess(name=name, target=service, *args,
                                              **kwargs, daemon=True)
        subprocess.start()
        self.subprocesses[subprocess.pid] = subprocess
        LOGGER.debug('Started subprocess', name=name)
        await subprocess.coro_join()
        if subprocess.exitcode == EmergencyStopException.EXIT_CODE:
            LOGGER.critical('Received emergency stop', name=name)
            raise EmergencyStopException()
        self.terminate(subprocess)
        del self.subprocesses[subprocess.pid]

    def terminate(self, subprocess, terminate_timeout=2):
        subprocess.terminate()
        LOGGER.warn('Sent SIGTERM to subprocess', name=subprocess.name)
        subprocess.join(terminate_timeout)
        time.sleep(0.05)  # Allow "exitcode" to set.
        if subprocess.is_alive():
            subprocess.kill()
            LOGGER.critical('Sent SIGKILL to subprocess, unabel to shut down gracefully',
                            name=name, timeout=terminate_timeout)
        else:
            LOGGER.debug('Subprocess terminated cleanly', name=subprocess.name)

    async def spin(self, **services):
        LOGGER.info('Starting services ...', services=list(services.keys()))
        subprocesses = []
        for name, config in services.items():
            replicas = config.get('replicas', 1)
            for replica in range(replicas):
                service = SERVICES[name]()
                subprocesses.append(self.spawn(f'{name}-{replica}', service, **config))
        await asyncio.wait(subprocesses, return_when=asyncio.FIRST_COMPLETED)


@dataclasses.dataclass
class Runtime:
    """
    The Runtime engine.
    """
    config_file: str
    log_pretty: bool
    log_level: str

    def configure_logging(self):
        logging.basicConfig(
            format="%(message)s",
            level=self.log_level,
        )

        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]

        if self.log_pretty:
            renderer = structlog.dev.ConsoleRenderer(pad_event=50)
        else:
            renderer = structlog.processors.JSONRenderer()
            processors.append(structlog.stdlib.render_to_log_kwargs)
        processors.append(renderer)
        logging.getLogger('asyncio').disabled = True

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    async def main(self):
        try:
            self.configure_logging()
            LOGGER.debug(f'Runtime v{get_version()}')
            LOGGER.debug(f'Configured logging', min_level=self.log_level, pretty=self.log_pretty)

            async with aiofiles.open(self.config_file) as config_file:
                config = yaml.load(await config_file.read())
            LOGGER.debug(f'Read configuration from disk', path=self.config_file)

            with ServiceSupervisor() as supervisor:
                await supervisor.spin(**config['services'])
        except Exception as exc:
            LOGGER.critical('Error reached the top of the call stack')
            raise exc
        else:
            LOGGER.debug('Runtime is exiting')
