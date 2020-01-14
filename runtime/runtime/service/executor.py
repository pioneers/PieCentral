import asyncio
import enum
import dataclasses
import types
from typing import Optional

import aiofiles
import structlog

from runtime.service.base import Service
from runtime.util.exception import EmergencyStopException


LOGGER = structlog.get_logger()


class Mode(enum.IntEnum):
    IDLE = enum.auto()
    AUTO = enum.auto()
    TELEOP = enum.auto()
    ESTOP = enum.auto()


class Alliance(enum.IntEnum):
    BLUE = enum.auto()
    GOLD = enum.auto()


class Actions:
    @staticmethod
    async def sleep(seconds):
        await asyncio.sleep(seconds)


@dataclasses.dataclass
class Robot:
    service: Service

    def testing_mode(self, enabled: bool = False):
        pass


class Gamepad:
    pass


@dataclasses.dataclass
class Field:
    service: Service

    @property
    def alliance(self):
        return self.service.alliance.name


async def load_student_code(module_name):
    pass


@dataclasses.dataclass
class ExecutorService(Service):
    access: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    alliance: Alliance = None
    mode: Mode = Mode.IDLE
    execution: Optional[asyncio.Task] = None

    async def set_alliance(self, alliance: Alliance = None):
        async with self.access:
            self.alliance = alliance

    def stop_execution(self):
        if self.execution:
            self.execution.cancel()
            self.execution = None

    async def set_mode(self, module_name: str, mode: Mode = Mode.IDLE):
        """
        Set the mode and start/stop executing student code.

        When `Mode.AUTO` or `Mode.TELEOP` is set, any code that is executing is
        cancelled and a new task is started.

        Raises::
            EmergencyStopException: When an e-stop is triggered.
        """
        async with self.access:
            self.mode = mode
            self.stop_execution()
            if mode is Mode.ESTOP:
                raise EmergencyStopException
            elif mode is not Mode.IDLE:
                student_code = await load_student_code(module_name)
                execute = self.execute_auto if self.mode is Mode.AUTO else self.execute_teleop
                self.execution = asyncio.create_task(execute(student_code))

    async def execute_auto(self, student_code: types.ModuleType):
        pass

    async def execute_teleop(self, student_code: types.ModuleType):
        pass

    async def main(self, config):
        while True:
            LOGGER.debug('Waiting ...')
            request = await self.connections['fieldcontrol'].recv()
            LOGGER.debug('Received request', request=request)
            await self.connections['fieldcontrol'].send({})
            LOGGER.debug('SEnt response')
