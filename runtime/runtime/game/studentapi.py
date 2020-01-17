import abc
import asyncio
import dataclasses
import enum
import typing


class StudentAPI(abc.ABC):
    pass


class Mode(enum.Enum):
    IDLE = enum.auto()
    AUTO = enum.auto()
    TELEOP = enum.auto()
    ESTOP = enum.auto()


class Alliance(enum.Enum):
    BLUE = enum.auto()
    GOLD = enum.auto()


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


class Gamepad(StudentAPI):
    def get_value(self, param: str, gamepad_id: str = None):
        pass


@dataclasses.dataclass
class Robot(StudentAPI):
    def get_value(self, device_id: typing.Union[str, int], param: str):
        pass

    def set_value(self, device_id: typing.Union[str, int], param: str, value):
        pass

    def testing_mode(self, enabled: bool = False):
        pass
