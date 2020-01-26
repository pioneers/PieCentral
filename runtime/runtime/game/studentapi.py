import abc
import asyncio
import collections
import dataclasses
import enum
import os
from numbers import Real
import shutil
import tempfile
import typing
import uuid

import aiofiles
import structlog
import yaml

from runtime.messaging.device import DeviceBuffer
from runtime.util.exception import RuntimeExecutionError


class DeviceAliasManager(collections.UserDict):
    def __init__(self, filename: str, persist_timeout: Real):
        super().__init__()
        self.filename, self.persist_timeout = filename, persist_timeout
        self.persisting = asyncio.Lock()
        asyncio.create_task(asyncio.wait_for(self.load_initial_aliases(), self.persist_timeout))

    async def load_initial_aliases(self):
        async with self.persisting:
            try:
                async with aiofiles.open(self.filename) as alias_file:
                    self.data.update(yaml.load(await alias_file.read()))
                LOGGER.debug('Loaded initial aliases', aliases=self.data)
            except FileNotFoundError:
                pass

    async def persist_aliases(self):
        async with self.persisting:
            tmp_path = os.path.join(tempfile.gettempdir(), f'dev-aliases-{uuid.uuid4()}')
            async with aiofiles.open(tmp_path, mode='w+') as alias_file:
                await alias_file.write(yaml.dump(self.data, default_flow_style=False))
            try:
                shutil.move(tmp_path, self.filename)
                LOGGER.debug('Persisted device aliases', aliases=self.data)
            finally:
                try:
                    os.unlink(tmp_path)
                    LOGGER.error('Failed to move temporary device aliases file')
                except OSError:
                    pass

    def __setitem__(self, name: str, uid: typing.Union[str, int]):
        super().__setitem__(name, uid)
        asyncio.create_task(asyncio.wait_for(self.persist_aliases(), self.persist_timeout))

    def __delitem__(self, name: str):
        super().__delitem__(name)
        asyncio.create_task(asyncio.wait_for(self.persist_aliases(), self.persist_timeout))


class StudentAPI(abc.ABC):
    """ Base abstract type for all interfaces exposed to student code. """


class Mode(enum.Enum):
    IDLE = enum.auto()
    AUTO = enum.auto()
    TELEOP = enum.auto()
    ESTOP = enum.auto()


class Alliance(enum.Enum):
    BLUE = enum.auto()
    GOLD = enum.auto()


@dataclasses.dataclass
class Actions(StudentAPI):
    @staticmethod
    async def sleep(seconds):
        await asyncio.sleep(seconds)


@dataclasses.dataclass
class Match(StudentAPI):
    alliance: Alliance = None
    mode: Mode = Mode.IDLE

    def as_dict(self):
        return {'alliance': self.alliance.name, 'mode': self.mode.name}


@dataclasses.dataclass
class Gamepad(StudentAPI):
    mode: Mode
    device_buffers: typing.Mapping[str, DeviceBuffer]
    logger: structlog.BoundLoggerBase = dataclasses.field(default_factory=structlog.get_logger)

    def get_value(self, param: str, gamepad_id: str = 0):
        if self.mode is not Mode.TELEOP:
            raise RuntimeExecutionError(f'Cannot use Gamepad during {self.mode.name}',
                                        mode=self.mode.name, gamepad_id=gamepad_id,
                                        param=param)
        try:
            buffer = self.device_buffers[f'gamepad-{gamepad_id}']
            return buffer.struct.get_current(param)
        except KeyError:
            self.logger.warn('Unrecognized Gamepad', gamepad_id=gamepad_id)
        except AttributeError:
            self.logger.warn('Unknown parameter', param=param)


@dataclasses.dataclass(init=False)
class Robot(StudentAPI):
    def __init__(self, action_executor, aliases: DeviceAliasManager):
        self.action_executor, self.aliases = action_executor, aliases

    def run(self, action, *args, timeout: float = 15):
        # TODO: use timeout parameter
        self.action_executor.register_action_threadsafe(action, *args)

    def is_running(self, action):
        self.action_executor.is_running(action)

    def get_value(self, device_id: typing.Union[str, int], param: str):
        pass

    def set_value(self, device_id: typing.Union[str, int], param: str, value):
        pass

    def testing_mode(self, enabled: bool = False):
        pass

    async def spin(self):
        pass
