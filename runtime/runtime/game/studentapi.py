import abc
import asyncio
import collections
import dataclasses
import enum
import os
from numbers import Real
import shutil
import tempfile
import threading
import typing
import uuid

import aiofiles
import structlog
import yaml

from runtime.messaging.device import DeviceBuffer
from runtime.util.exception import RuntimeExecutionError


class DeviceAliasManager(collections.UserDict):
    def __init__(self, filename: str, persist_timeout: Real,
                 logger: structlog.BoundLoggerBase = None):
        super().__init__()
        self.filename, self.persist_timeout = filename, persist_timeout
        self.logger = logger or structlog.get_logger()
        self.persisting = asyncio.Lock()

    async def load_initial_aliases(self):
        async with self.persisting:
            try:
                async with aiofiles.open(self.filename) as alias_file:
                    self.data.update(yaml.load(await alias_file.read()))
                self.logger.debug('Loaded initial aliases', aliases=self.data)
            except FileNotFoundError:
                pass

    async def persist_aliases(self):
        async with self.persisting:
            tmp_path = os.path.join(tempfile.gettempdir(), f'dev-aliases-{uuid.uuid4()}')
            async with aiofiles.open(tmp_path, mode='w+') as alias_file:
                await alias_file.write(yaml.dump(self.data, default_flow_style=False))
            try:
                shutil.move(tmp_path, self.filename)
                self.logger.debug('Persisted device aliases', aliases=self.data)
            finally:
                try:
                    os.unlink(tmp_path)
                    self.logger.error('Failed to move temporary device aliases file')
                except OSError:
                    pass

    def __setitem__(self, name: str, uid: typing.Union[str, int]):
        super().__setitem__(name, str(uid))
        asyncio.create_task(asyncio.wait_for(self.persist_aliases(), self.persist_timeout))

    def __delitem__(self, name: str):
        super().__delitem__(name)
        asyncio.create_task(asyncio.wait_for(self.persist_aliases(), self.persist_timeout))


DeviceBufferMap = typing.Mapping[str, DeviceBuffer]


class StudentAPI(abc.ABC):
    """ Base abstract type for all interfaces exposed to student code. """


@dataclasses.dataclass
class DeviceAPI(StudentAPI):
    device_buffers: DeviceBufferMap
    logger: structlog.BoundLoggerBase

    def _get_device_buffer(self, device_uid: str):
        try:
            return self.device_buffers[device_uid]
        except KeyError:
            self.logger.warn('Unrecognized device', device_uid=device_uid)

    def get_value(self, device_uid: str, param: str):
        device = self._get_device_buffer(device_uid)
        if device:
            try:
                return device.struct.get_current(param)
            except AttributeError:
                self.logger.warn(
                    'Unrecognized or unreadable parameter',
                    device_uid=device_uid,
                    device_type=device.struct.__class__.__name__,
                    param=param,
                )


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
class Gamepad(DeviceAPI):
    mode: Mode

    def get_value(self, param: str, gamepad_id: str = 0):
        if self.mode is not Mode.TELEOP:
            raise RuntimeExecutionError(f'Cannot use Gamepad during {self.mode.name}',
                                        mode=self.mode.name, gamepad_id=gamepad_id,
                                        param=param)
        return super().get_value(f'gamepad-{gamepad_id}', param)


@dataclasses.dataclass
class Robot(DeviceAPI):
    action_executor: threading.Thread
    aliases: DeviceAliasManager

    def run(self, action, *args, timeout: float = 30):
        self.action_executor.register_action_threadsafe(action, *args, timeout=timeout)

    def is_running(self, action):
        self.action_executor.is_running(action)

    def _normalize_device_uid(self, device_uid: typing.Union[str, int]) -> str:
        if isinstance(device_uid, str) and device_uid in self.aliases:
            device_uid = self.aliases[device_uid]
        else:
            device_uid = device_uid
        return f'smart-sensor-{device_uid}'

    def get_value(self, device_uid: typing.Union[str, int], param: str):
        return super().get_value(self._normalize_device_uid(device_uid), param)

    def set_value(self, device_uid: typing.Union[str, int], param: str, value):
        device = self._get_device_buffer(self._normalize_device_uid(device_uid))
        if device:
            try:
                device.struct.set_desired(param, value)
            except AttributeError:
                self.logger.warn(
                    'Unrecognized or read-only parameter',
                    device_uid=device_uid,
                    device_type=device.struct.__class__.__name__,
                    param=param,
                )

    def testing_mode(self, enabled: bool = False):
        pass

    async def spin(self):
        pass
