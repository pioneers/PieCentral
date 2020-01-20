import abc
import asyncio
import dataclasses
import enum
import typing

from runtime.util.exception import RuntimeExecutionError


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
    mode: Mode = None

    def as_dict(self):
        return {'alliance': self.alliance.name, 'mode': self.mode.name}


@dataclasses.dataclass
class Gamepad(StudentAPI):
    mode: Mode

    def get_value(self, param: str, gamepad_id: str = None):
        if self.mode is not Mode.TELEOP:
            raise RuntimeExecutionError(f'Cannot use Gamepad during {self.mode.name}',
                                        mode=self.mode.name, gamepad_id=gamepad_id,
                                        param=param)


@dataclasses.dataclass(init=False)
class Robot(StudentAPI):
    def __init__(self, action_executor):
        self.action_executor = action_executor

    def run(self, action, *args):
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
