import asyncio
import collections
import dataclasses
import functools
import time

import aiofiles
import aioprocessing
import backoff
import structlog
from schema import Schema, And, Use, Optional
import yaml
import zmq.asyncio

from runtime import get_version
from runtime.service import SERVICES
from runtime.service.base import Service
from runtime.monitoring.retry import Proxy

LOGGER = structlog.get_logger()


class SubprocessMonitor:
    def __init__(self, name: str, service: Service, *args, **kwargs):
        self.subprocess = aioprocessing.AioProcess(name=name, target=service, args=args, kwargs=kwargs)

    def terminate(self, timeout=2):
        self.subprocess.terminate()
        LOGGER.warn('Sent SIGTERM to subprocess', name=self.subprocess.name)
        self.subprocess.join(timeout)
        time.sleep(0.05)  # Wait for "exitcode" to set.
        if self.subprocess.is_alive():
            self.subprocess.kill()
            LOGGER.critical('Sent SIGKILL to subprocess, unable to shut down gracefully',
                            name=self.subprocess.name)

    async def spin(self):
        self.subprocess.start()
        LOGGER.info(f'Started subprocess {self.subprocess.name}')
        await self.subprocess.coro_join()
        raise ValueError()  # TODO: change exception type


class SubprocessManager(collections.UserDict):
    retry_policy = functools.partial(backoff.on_exception, backoff.constant, ValueError, interval=1)

    def make_retryable_subprocess(self, name: str, service: Service, *args, **kwargs):
        subprocess_factory = functools.partial(SubprocessMonitor, name, service, *args, **kwargs)
        retry_policies = collections.defaultdict(lambda: self.retry_policy)
        return Proxy(subprocess_factory, LOGGER, policies=retry_policies, cleanup=SubprocessMonitor.terminate)

    def add(self, service_name: str):
        service = SERVICES[service_name]()
        self[service_name] = [self.make_retryable_subprocess(service_name, service)]

    async def spin(self):
        LOGGER.info('Starting subprocesses')
        subprocesses = []
        for replicas in self.values():
            subprocesses.extend(replicas)
        tasks = [subprocess.spin() for subprocess in subprocesses]
        await asyncio.gather(*tasks)


@dataclasses.dataclass
class Runtime:
    config_file: str
    log_level: str
    subprocesses: SubprocessManager = SubprocessManager()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    async def main(self):
        LOGGER.debug(f'Runtime v{get_version()}')
        async with aiofiles.open(self.config_file) as config_file:
            config = yaml.load(await config_file.read())
        LOGGER.debug(f'Read config', path=self.config_file)

        # TODO
        import structlog.stdlib
        structlog.configure(
            processors=[
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.KeyValueRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
        )

        for service in config['services']:
            self.subprocesses.add(service)
        await self.subprocesses.spin()
