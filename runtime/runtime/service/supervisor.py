import abc
import asyncio
import dataclasses
import functools
from numbers import Real
import os
import pathlib
import typing

import aioprocessing
from aioprocessing.process import AioProcess
import aiozmq.rpc
import backoff
import structlog
import zmq

import runtime
from runtime.frame import Frame
from runtime.service import Service
from runtime.game import studentapi as api
from runtime.service.storage import Document, DocumentClient
from runtime.service.device import DeviceService
from runtime.util.exception import EmergencyStopException


@dataclasses.dataclass(init=False)
class SupervisorService(Service):
    device_names: Document

    def __init__(self, device_names: Document, *args, **kwargs):
        self.device_names = device_names
        super().__init__(*args, **kwargs)

    async def main(self):
        asyncio.create_task(super().main(), name='service-main')
        await asyncio.sleep(1)  # Wait for log relay to spin up
        self.logger.debug('Runtime supervisor started',
                          version=f'v{runtime.get_version()}',
                          pid=os.getpid())
        catalog = [device_type.__name__ for device_type in Frame.catalog.values()]
        self.logger.debug('Device catalog', catalog=catalog)

        address = await self.config.get('device.addresses.rpc')
        config_client = DocumentClient(self.address, namespace='config')
        device_service = DeviceService(address, config_client, debug=self.debug)
        await self.run_subprocess(device_service)

    async def run_subprocess(self, service: Service):
        """ Run a subprocess indefinitely. """
        subprocess = aioprocessing.AioProcess(name=service.__class__.__name__.lower(),
                                              target=service.bootstrap, daemon=True)
        subprocess.start()
        try:
            await subprocess.coro_join()
        finally:
            await self.terminate_subprocess(subprocess)

    async def terminate_subprocess(self, subprocess: AioProcess):
        """
        Terminate a subprocess using the SIGTERM (or SIGKILL) UNIX signals.

        If the subprocess does not exit within a timeout after receiving
        `SIGTERM`, the subprocess is forcefully terminated with `SIGKILL`
        through the OS. An ungraceful shutdown may leave the system in an
        inconsistent state.

        Arguments:
            subprocess: The subprocess to terminate.

        Raises::
            EmergencyStopException: If the subprocess triggers an emergency stop.
        """
        context = {'name': subprocess.name, 'pid': subprocess.pid}
        timeout = await self.config.get('supervisor.subprocess.timeout')
        subprocess.terminate()
        self.logger.warn('Sent SIGTERM to subprocess', **context, timeout=timeout)
        await subprocess.coro_join(timeout)
        await asyncio.sleep(0.05)  # Allow `exitcode` to set.

        if subprocess.is_alive():
            self.logger.critical('Unable to shutdown gracefully')
            subprocess.kill()
            self.logger.critical('Sent SIGKILL to subprocess', **context)
        else:
            self.logger.debug('Subprocess terminated cleanly', **context, exit_code=subprocess.exitcode)

        if subprocess.exitcode == EmergencyStopException.EXIT_CODE:
            self.logger.critical('Received emergency stop', **context)
            raise EmergencyStopException

    @aiozmq.rpc.method
    async def execute(self, mode: api.Mode, alliance: api.Alliance):
        pass

    @aiozmq.rpc.method
    async def challenge(self, challenges, seed: int) -> int:
        pass

    @aiozmq.rpc.method
    async def lint(self):
        pass
