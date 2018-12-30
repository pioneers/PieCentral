"""
runtime.store -- Runtime data storage
"""

import asyncio
import ctypes
import enum
import collections
from functools import lru_cache, reduce
import time
from typing import List
from runtime import __version__
import runtime.journal
from runtime.util import read_conf_file, RuntimeBaseException
from runtime.studentcode import *

LOGGER = runtime.journal.make_logger(__name__)


class Alliance(enum.Enum):
    BLUE = enum.auto()
    GOLD = enum.auto()
    UNKNOWN = enum.auto()


class StartingZone(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    VENDING = enum.auto()
    SHELF = enum.auto()
    UNKNOWN = enum.auto()


class Mode(enum.Enum):
    IDLE = enum.auto()
    AUTO = enum.auto()
    TELEOP = enum.auto()
    ESTOP = enum.auto()


def alias(keys: List[str], name: str):
    def decorator(cls):
        def get_nested(self):
            return reduce(lambda subdict, key: subdict.get(key) if subdict else None, keys, self)
        setattr(cls, name, property(get_nested))
        return cls
    return decorator


@alias(['options'], 'options')
@alias(['fieldcontrol'], 'field_params')
@alias(['devices', 'names'], 'device_names')
@alias(['devices', 'streamsubscribers'], 'stream_subs')
class StoreService(collections.UserDict):
    version_number_names = ('major', 'minor', 'patch')

    def __init__(self, options: dict):
        super().__init__()
        self.access = asyncio.Lock()
        self.update({
            'options': options,
            'fieldcontrol': {
                'alliance': Alliance.UNKNOWN,
                'startingzone': StartingZone.UNKNOWN,
                'mode': Mode.IDLE,
            },
            'devices': {
                'names': {},
            },
            'networking': {
                'streamsubscribers': [],
            }
        })

        try:
            self.device_names.update(read_conf_file(options['dev_names']))
        except (FileNotFoundError, RuntimeBaseException):
            LOGGER.warning('Unable to read Smart Sensor names.')

    def get_version(self):
        return dict(zip(self.version_number_names, __version__))

    def get_time(self):
        return time.time()

    async def get_options(self):
        async with self.access:
            return self.options

    async def set_options(self, persist=True, **options):
        async with self.access:
            self.options.update(options)
            if persist:
                with open(self.options['config']) as options_file:
                    write_conf_file(options_file, self.options)

    async def get_field_parameters(self):
        async with self.access:
            return {name: value.name.lower() for name, value in self.field_params.items()}

    async def set_alliance(self, alliance: str):
        async with self.access:
            self.field_params['alliance'] = Alliance.__members__[alliance.upper()]

    async def set_starting_zone(self, zone: str):
        async with self.access:
            self.field_params['startingzone'] = StartingZone.__members__[zone.upper()]

    async def set_mode(self, mode: str):
        async with self.access:
            # TODO: dispatch to executor
            self.field_params['mode'] = Mode.__members__[mode.upper()]

    async def run_coding_challenge(self, seed: int) -> int:
        async def get_student_solution(f, seed: int) -> int:
            return f(seed)
        challenge_functions = [tennis_ball, remove_duplicates, rotate, next_fib, most_common, get_coins]
        solution = seed
        for f in challenge_functions:
            try:
                solution = await asyncio.wait_for(get_student_solution(f, solution), timeout=1.0)
            except asyncio.TimeoutError as e:
                LOGGER.error(str(f) + " took too long to provide an answer")
                raise e
        return solution

    async def write_device_names(self):
        with open(self.options['dev_names']) as dev_name_file:
            write_conf_file(dev_name_file, self.device_names)

    async def get_device_names(self):
        async with self.access:
            return self.device_names

    async def set_device_name(self, name: str, uid: str):
        async with self.access:
            self.device_names[uid] = name
            await self.write_device_names()

    async def del_device_name(self, uid: str):
        async with self.access:
            del self.device_names[uid]
            await self.write_device_names()


# def validate_param_value(param: Parameter, value):
#     ctype = getattr(ctypes, f'c_{param.type}')
#     ctype(value)  # Will raise a ``TypeError`` if the value is not correct.
#     if ctype in CTYPES_NUMERIC and not param.lower <= value <= param.upper:
#         raise RuntimeBaseException(
#             'Parameter value not in bounds.',
#             param_name=param.name,
#             param_value=value,
#             bounds=(param.lower, param.upper),
#         )
#     if value not in param.choices:
#         raise RuntimeBaseException(
#             'Parameter value is not a valid choice.',
#             param_name=param.name,
#             param_value=value,
#             choices=param.choices,
#         )
