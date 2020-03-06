"""
The student API allows student code to interact with the robot.

When the student code module is loaded, interfaces are monkey-patched into
student code with the names student code expects are in its scope.
"""

import abc
import asyncio
import collections
import dataclasses
import enum
import functools
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

from runtime.messaging.device import DeviceBuffer, DeviceMapping
from runtime.monitoring import log
from runtime.util.exception import RuntimeBaseException, RuntimeExecutionError


__all__ = ['DeviceAliasManager', 'safe', 'Mode', 'Alliance', 'Actions', 'Match',
           'Gamepad', 'Robot']


Action = typing.Callable[..., None]
LOG_CAPTURE = log.LogCapture()
LOGGER = log.get_logger(LOG_CAPTURE)


class DeviceAliasManager(collections.UserDict):
    """
    Maps human-readable device aliases to UIDs.

    As soon as this mapping is mutated, a task is scheduled to write the updated
    mapping to disk immediately. Since mutations are rare, there is no need to
    cache changes and batch filesystem writes.

    The alias manager does not validate the UIDs, since devices might be
    temporarily disconnected from the robot.

    Attributes:
        filename: The YAML file to persist to.
        persist_timeout: The timeout to write the aliases file.
        logger: A logger instance.
        persisting: A lock to ensure persistence operations are atomic (sequential).
    """

    def __init__(self, filename: str, persist_timeout: Real = 60,
                 logger: structlog.BoundLoggerBase = None):
        super().__init__()
        self.filename, self.persist_timeout = filename, persist_timeout
        self.logger = logger or structlog.get_logger()
        self.persisting = asyncio.Lock()

    async def load_existing_aliases(self):
        """
        Populate this manager with existing device aliases.

        Ignore a missing aliases file (there is nothing to populate).
        """
        async with self.persisting:
            try:
                async with aiofiles.open(self.filename) as alias_file:
                    aliases = yaml.safe_load(await alias_file.read())
                    if not isinstance(aliases, dict):
                        raise yaml.error.YAMLError
                    for alias, uid in aliases.items():
                        self.data[alias] = str(uid)
                self.logger.debug('Loaded initial aliases', aliases=self.data)
            except FileNotFoundError:
                self.logger.warning('Device aliases do not yet exist')
            except yaml.error.YAMLError:
                self.logger.error('Unable to read aliases file (possible corruption)')

    async def persist_aliases(self):
        """
        Write the state of this manager to disk.

        The manager writes the aliases to a temporary file before atomically
        moving the temporary file to the desired location (using the ``rename``
        semantics of POSIX). This ensures that even if Runtime crashes during a
        write, the aliases file will always contain well-formatted YAML.

        The mapping is written as an object of strings to strings.
        """
        async with self.persisting:
            tmp_path = os.path.join(tempfile.gettempdir(), f'dev-aliases-{uuid.uuid4()}.yaml')
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


def safe(api_method: typing.Callable):
    """
    A decorator that traps and logs Runtime-specific exceptions.

    This prevents exceptions from propogating up the call stack and
    interrupting the student code caller. For example, setting a nonexistent
    parameter should not prevent subsequent statements from executing.

    Because a safe API method returns ``None`` on an exception, student code
    may still fail to proceed.
    """
    @functools.wraps(api_method)
    def api_wrapper(*args, **kwargs):
        try:
            return api_method(*args, **kwargs)
        except RuntimeBaseException as exc:
            LOGGER.error(str(exc), exc_info=exc, **exc.context)
    return api_wrapper


class StudentAPI(abc.ABC):
    """ Base abstract type for all callable interfaces exposed to student code. """


@dataclasses.dataclass
class DeviceAPI(StudentAPI):
    """
    An API that exposes access to a collection of devices (gamepads or sensors).

    Attributes:
        device_buffers: A mapping of unique identifiers (not necessarily UIDs)
            to device buffers.
    """
    device_buffers: DeviceMapping

    def _get_device_buffer(self, device_uid: str) -> DeviceBuffer:
        """ Retrieve a device buffer, or raise an exception if not found. """
        try:
            return self.device_buffers[device_uid]
        except KeyError as exc:
            raise RuntimeExecutionError('Unrecognized device', device_uid=device_uid) from exc

    def _get_value(self, device_uid: str, param: str) -> typing.Any:
        """ Read a device parameter. """
        device = self._get_device_buffer(device_uid)
        try:
            return device.struct.get_current(param)
        except AttributeError as exc:
            raise RuntimeExecutionError(
                'Unrecognized or unreadable parameter',
                device_uid=device_uid,
                device_type=type(device.struct).__name__,
                param=param,
            ) from exc


class Mode(enum.Enum):
    """
    The mode represents the execution state of the robot.

    Attributes:
        IDLE: Student code is not executing.
        AUTO: Autonomous mode. Gamepad usage is disallowed.
        TELEOP: Tele-operation mode. Gamepad usage is allowed.
        ESTOP: Emergency stop. Immediately triggers a Runtime exit.
    """
    IDLE = enum.auto()
    AUTO = enum.auto()
    TELEOP = enum.auto()
    ESTOP = enum.auto()


class Alliance(enum.Enum):
    """
    The alliance are the teams playing the game.

    Attributes:
        BLUE: The blue team.
        GOLD: The gold team.
    """
    BLUE = enum.auto()
    GOLD = enum.auto()


@dataclasses.dataclass
class Actions(StudentAPI):
    """ Miscellaneous asynchronous callables. """
    @staticmethod
    @safe
    async def sleep(seconds: Real):
        """ Suspend execution of this awaitable. """
        await asyncio.sleep(seconds)


@dataclasses.dataclass
class Match(StudentAPI):
    """ The current match state. """
    alliance: typing.Optional[Alliance] = None
    mode: Mode = Mode.IDLE

    def as_dict(self) -> dict:
        """ Export this match as a serializable dictionary. """
        return {'alliance': self.alliance.name, 'mode': self.mode.name}


@dataclasses.dataclass
class Gamepad(DeviceAPI):
    """
    The API for accessing gamepads.

    Attributes:
        mode: The execution state of the robot.
    """
    mode: Mode

    @safe
    def get_value(self, param: str, gamepad_id: int = 0):
        """
        Get a gamepad parameter if the robot is in teleop.

        Attributes:
            param: The name of the parameter to read.
            gamepad_id: The gamepad index (defaults to the first gamepad).
        """
        if self.mode is not Mode.TELEOP:
            raise RuntimeExecutionError(f'Cannot use Gamepad during {self.mode.name}',
                                        mode=self.mode.name, gamepad_id=gamepad_id,
                                        param=param)
        return super()._get_value(f'gamepad-{gamepad_id}', param)


ParameterValue = typing.Union[str, Real, bool]


@dataclasses.dataclass
class Robot(DeviceAPI):
    """
    The API for accessing the robot and its sensors.

    Attributes:
        action_executor: An action executor.
        aliases: A device alias manager.
    """
    action_executor: threading.Thread
    aliases: DeviceAliasManager

    @safe
    def run(self, action: Action, *args, timeout: Real = 300):
        """ Schedule an action (coroutine function) for execution in a separate thread. """
        self.action_executor.register_action_threadsafe(action, *args, timeout=timeout)

    @safe
    def is_running(self, action: Action) -> bool:
        """ Check whether an action is currently executing. """
        self.action_executor.is_running(action)

    def _normalize_device_uid(self, device_uid: typing.Union[str, int]) -> str:
        """ Translate device aliases into UIDs and return a device mapping key. """
        device_uid = str(device_uid)
        if device_uid in self.aliases:
            device_uid = self.aliases[device_uid]
        return f'smart-sensor-{device_uid}'

    @safe
    def get_value(self, device_uid: typing.Union[str, int], param: str) -> ParameterValue:
        """ Get a smart sensor parameter. """
        return super()._get_value(self._normalize_device_uid(device_uid), param)

    @safe
    def set_value(self, device_uid: typing.Union[str, int], param: str, value: ParameterValue):
        """ Set a smart sensor parameter. """
        device = self._get_device_buffer(self._normalize_device_uid(device_uid))
        try:
            device.struct.set_desired(param, value)
        except AttributeError as exc:
            raise RuntimeExecutionError(
                'Unrecognized or read-only parameter',
                device_uid=device_uid,
                device_type=type(device.struct).__name__,
                param=param,
            ) from exc
