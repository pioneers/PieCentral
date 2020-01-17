import asyncio
import collections
import dataclasses
import functools
import logging
import operator
import time
from typing import Any, Callable, Coroutine, Mapping, Set, Sequence
import uuid

import aiofiles
import aioprocessing
import backoff
import structlog
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass
import yaml
import zmq.asyncio

from runtime import get_version
from runtime.messaging.device import load_device_types
from runtime.service import SERVICES
from runtime.service.base import Service
from runtime.monitoring import retry, log
from runtime.util.exception import EmergencyStopException


LOGGER = structlog.get_logger()


def terminate_subprocess(subprocess, timeout: float = 2):
    context = {'name': subprocess.name, 'pid': subprocess.pid}
    subprocess.terminate()
    LOGGER.warn('Sent SIGTERM to subprocess', **context, terminate_timeout=timeout)
    subprocess.join(timeout)
    time.sleep(0.05)  # Allow `exitcode` to set.

    if subprocess.is_alive():
        subprocess.kill()
        LOGGER.critical('Sent SIGKILL to subprocess '
                        '(unable to terminate gracefully)', **context)
    else:
        LOGGER.debug('Subprocess terminated cleanly', **context)

    if subprocess.exitcode == EmergencyStopException.EXIT_CODE:
        LOGGER.critical('Received emergency stop', name=name)
        raise EmergencyStopException


@backoff.on_predicate(backoff.constant, interval=1, max_tries=5, logger=LOGGER)
async def run_subprocess(service, config):
    name = f'{service.__name__.lower()}-{uuid.uuid4()}'
    subprocess = aioprocessing.AioProcess(name=name, target=service(config),
                                          daemon=config['daemon'])
    subprocess.start()
    try:
        await subprocess.coro_join()
    finally:
        terminate_subprocess(subprocess)


async def spin(service_config):
    """ Spin up, then clean up, all processes. """
    LOGGER.info('Starting services ...', services=list(service_config))
    subprocesses = []
    for name, config in service_config.items():
        service = SERVICES.get(name)
        if not service:
            raise RuntimeBaseException('Service not found', name=name)
        config = service.get_config_schema().validate(config)
        for _ in range(config['replicas']):
            subprocesses.append(run_subprocess(service, config))
    done, pending = await asyncio.wait(subprocesses, return_when=asyncio.FIRST_COMPLETED)
    for subprocess in pending:
        subprocess.cancel()


async def start(srv_config_path: str, dev_schema_path: str, log_level: str, log_pretty: bool):
    try:
        log.configure_logging(log_level, log_pretty)
        LOGGER.debug(f'Runtime v{get_version()}')
        LOGGER.debug(f'Configured logging', level=log_level, pretty=log_pretty)

        async with aiofiles.open(srv_config_path) as config_file:
            service_config = yaml.load(await config_file.read())
        LOGGER.debug(f'Read configuration from disk', srv_config_path=srv_config_path)

        async with aiofiles.open(dev_schema_path) as schema_file:
            dev_schema = yaml.load(await schema_file.read())
        load_device_types(dev_schema)
        LOGGER.debug(f'Read device schema from disk', dev_schema_path=dev_schema_path)

        await spin(service_config)
    except Exception as exc:
        LOGGER.critical('Error reached the top of the call stack')
        raise exc
    finally:
        LOGGER.debug('Runtime is exiting')
