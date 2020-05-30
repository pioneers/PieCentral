"""
The supervisor runs all subprocesses.
"""

import asyncio
import collections
import dataclasses
import functools
import logging
from numbers import Real
import operator
import threading
from typing import Any, Callable, Coroutine, Mapping, Set, Sequence
import uuid

import aiofiles
import aioprocessing
import backoff
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass
import yaml
import zmq.asyncio
from zmq.devices import ThreadDevice

from runtime import get_version
from runtime.messaging.connection import Connection
from runtime.messaging.device import load_device_types, LOG_CAPTURE as DEV_LOG_CAPTURE
from runtime.service import SERVICES
from runtime.service.base import Service
from runtime.monitoring import log
from runtime.util.exception import EmergencyStopException


async def spin(configs: Mapping[str, dict]):
    """
    Spin up, then clean up, all subprocesses.

    As soon as one subprocess exits, all of them are terminated. Subprocesses
    are not restarted on an individual basis because state may be distributed
    across the services, which can become inconsistent if some but not all
    subprocesses are restarted.

    Arguments:
        configs: A map from service names to their configurations (see each
            service class for the configuration schema).
    """
    LOGGER.info('Starting services ...', services=list(configs))
    subprocesses = []
    for name, config in configs.items():
        service = SERVICES.get(name)
        if not service:
            raise RuntimeBaseException('Service not found', name=name)
        config = service.get_config_schema().validate(config)
        for _ in range(config['replicas']):
            subprocesses.append(run_subprocess(service, config))
    done, pending = await asyncio.wait(subprocesses, return_when=asyncio.FIRST_COMPLETED)
    for subprocess in pending:
        subprocess.cancel()


async def start(
        log_level: str,
        log_pretty: str,
        log_frontend: str,
        log_backend: str,
        srv_config_path: str,
        dev_schema_path: str,
        max_retries: int,
        retry_interval: Real):
    """
    Start the subprocess supervisor.

    Arguments:
        log_level: How verbose the log to standard output should be.
        log_pretty: Whether log records should be prettified when printed.
        srv_config_path: The path to the service configuration.
        dev_schema_path: The path to the device schema.
        max_retries: The maximum number of times to restart all the
            subprocesses before the supervisor exits.
        retry_interval: The duration between retries.
    """
    try:
        await initialize_log(log_level, log_pretty, log_frontend, log_backend)
        LOGGER.debug(f'Runtime v{get_version()}')
        LOGGER.debug(f'Configured logging', level=log_level, pretty=log_pretty)

        async with aiofiles.open(srv_config_path) as config_file:
            service_config = yaml.safe_load(await config_file.read())
        LOGGER.debug(f'Read configuration from disk', srv_config_path=srv_config_path)

        async with aiofiles.open(dev_schema_path) as schema_file:
            dev_schema = yaml.load(await schema_file.read())
        load_device_types(dev_schema)
        LOGGER.debug(f'Read device schema from disk', dev_schema_path=dev_schema_path)

        make_retryable = backoff.on_exception(
            backoff.constant,
            Exception,
            interval=retry_interval,
            max_tries=max_retries,
            logger=LOGGER,
        )
        await make_retryable(spin)(service_config)
    except Exception as exc:
        LOGGER.critical('Error reached the top of the call stack')
        raise exc
    finally:
        LOGGER.debug('Runtime is exiting')
