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
from schema import Schema, And, Use, Optional
import yaml
import zmq.asyncio

from runtime import get_version
from runtime.service import SERVICES
from runtime.service.base import Service
from runtime.monitoring import retry, log
from runtime.util import accept_decorators
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
        raise EmergencyStopException()


@backoff.on_predicate(backoff.constant, interval=1, max_tries=5, logger=LOGGER)
async def run_subprocess(name, config):
    subprocess = aioprocessing.AioProcess(
        name=f'{name}-{uuid.uuid4()}',
        target=SERVICES[name](),
        args=(config,),
        daemon=True,
    )
    subprocess.start()
    try:
        await subprocess.coro_join()
    finally:
        terminate_subprocess(subprocess)


async def spin(services):
    LOGGER.info('Starting services ...', services=list(services))
    subprocesses = []
    for name, config in services.items():
        for _ in range(config['replicas']):
            subprocesses.append(run_subprocess(name, config))
    done, pending = await asyncio.wait(subprocesses, return_when=asyncio.FIRST_COMPLETED)
    for subprocess in pending:
        pending.cancel()


async def start(config_path: str, log_level: str, log_pretty: bool):
    try:
        log.configure_logging(log_level, log_pretty)
        LOGGER.debug(f'Runtime v{get_version()}')
        LOGGER.debug(f'Configured logging', level=log_level, pretty=log_pretty)

        async with aiofiles.open(config_path) as config_file:
            config = yaml.load(await config_file.read())
        LOGGER.debug(f'Read configuration from disk', config_path=config_path)

        await spin(config['services'])
    except Exception as exc:
        LOGGER.critical('Error reached the top of the call stack')
        raise exc
    else:
        LOGGER.debug('Runtime is exiting')
