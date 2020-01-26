import asyncio
import collections
import ctypes
import dataclasses
import enum
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.managers import SharedMemoryManager
import time
from typing import Callable, Iterable, List, Union

import cachetools
import yaml
import zmq
from schema import And, Optional, Regex, Schema, Use
import structlog

from runtime.messaging.routing import Connection
from runtime.util import VALID_NAME
from runtime.util.exception import RuntimeBaseException


LOGGER = structlog.get_logger()
# The Smart Sensor protocol uses little Endian byte order (least-significant byte first).
Structure = ctypes.LittleEndianStructure


@cachetools.cached(cache={})
def make_timestamped_parameter(param_type) -> type:
    class TimestampedParameter(Structure):
        _fields_ = [
            ('value', param_type),
            ('last_updated', ctypes.c_double),
        ]

        def __setattr__(self, name: str, value):
            if name == 'value':
                self.last_updated = time.time()
            # TODO: validate parameter bounds? or saturate
            super().__setattr__(name, value)
    return TimestampedParameter


class SmartSensorUID(Structure):
    _pack_ = 1  # Ensure the fields are byte-aligned (pack as densely as possible)
    _fields_ = [
        ('device_type', ctypes.c_uint16),
        ('year', ctypes.c_uint8),
        ('id', ctypes.c_uint64),
    ]

    def to_int(self):
        return (self.device_type << 72) | (self.year << 64) | self.id


def get_field_bytes(structure: ctypes.Structure, field_name: str) -> bytes:
    field_description = getattr(type(structure), field_name)
    field_ref = ctypes.byref(structure, field_description.offset)
    return ctypes.string_at(field_ref, field_description.size)


class DeviceStructure(Structure):
    """
    The state of a device with readable/writeable parameters.

    Note::
        A "device" is more general than a "Smart Sensor", which is a special
        kind of "device". For example, gamepads are also treated as "devices".
    """
    Parameter = collections.namedtuple(
        'Parameter',
        ['name', 'type', 'lower', 'upper', 'readable', 'writeable'],
        defaults=[float('-inf'), float('inf'), True, False],
    )

    SMART_SENSOR_MAX_PARAMETERS: int = 16
    SMART_SENSOR_RESET = 0x0000

    @classmethod
    def _normalize_param_id(cls, param_id: Union[int, str]) -> str:
        return param_id if isinstance(param_id, str) else cls._params[param_id].name

    def get_current(self, param_name: str):
        return getattr(self, f'current_{param_name}').value

    def set_desired(self, param_name: str, value):
        getattr(self, f'desired_{param_name}').value = value
        self.dirty |= 1 << self._param_ids[param_name]

    def set_current(self, param_name: str, value):
        getattr(self, f'current_{param_name}').value = value

    @classmethod
    def get_parameters(cls, bitmap: int) -> Iterable[str]:
        for i in range(len(cls._params)):
            if (bitmap >> i) & 0b1:
                yield cls._params[i]

    @classmethod
    def make_type(cls: type, name: str, type_id: int, params: List[Parameter], *extra_fields):
        fields = list(extra_fields)
        for param in params:
            ctype = make_timestamped_parameter(param.type)
            fields.extend([(f'current_{param.name}', ctype), (f'desired_{param.name}', ctype)])
        return type(name, (cls, ), {
            '_params': params,
            '_param_ids': {param.name: index for index, param in enumerate(params)},
            '_fields_': fields,
            'type_id': type_id,
        })

    @classmethod
    def make_smart_sensor_type(cls: type, name: str, type_id: int, params: List[Parameter]):
        """
        Make a device type with extra fields to handle the Smart Sensor protocol.

        The extra fields included are:
          * `write`: A bitmap indicating which parameters should be written.
          * `read`: A bitmap indicating which parameters should be read.
          * `delay`: The current subscription period.
          * `subscription`: A bitmap of the parameters the Smart Sensor consumer
            is subscribed to.
          * `uid`: The unique identifier of the Smart Sensor.
        """
        if len(params) > DeviceStructure.SMART_SENSOR_MAX_PARAMETERS:
            raise RuntimeBaseException('Maxmimum number of Smart Sensor parameters exceeded')
        extra_fields = [
            ('write', ctypes.c_uint16),
            ('read', ctypes.c_uint16),
            ('delay', ctypes.c_uint16),
            ('subscription', ctypes.c_uint16),
            ('uid', SmartSensorUID),
        ]
        return DeviceStructure.make_type(name, type_id, params, *extra_fields)


DEVICE_SCHEMA = Schema({
    And(Use(str), VALID_NAME): {        # Protocol name
        And(Use(str), VALID_NAME): {    # Device name
            'id': And(Use(int), lambda type_id: 0 <= type_id < 0xFFFF),
            'params': [{
                'name': Use(str),
                'type': And(Use(str), Use(lambda dev_type: getattr(ctypes, f'c_{dev_type}'))),
                Optional('lower'): Use(float),
                Optional('upper'): Use(float),
                Optional('readable'): Use(bool),
                Optional('writeable'): Use(bool),
            }]
        }
    }
})
DEVICES = {}


def load_device_types(schema: str, smart_sensor_protocol: str = 'smartsensor'):
    schema = DEVICE_SCHEMA.validate(schema)
    for protocol, devices in schema.items():
        DEVICES[protocol] = {}
        if protocol == smart_sensor_protocol:
            make_device_type = DeviceStructure.make_smart_sensor_type
        else:
            make_device_type = DeviceStructure.make_type
        for device_name, device_conf in devices.items():
            params = [DeviceStructure.Parameter(**param_conf)
                      for param_conf in device_conf['params']]
            type_id = device_conf['id']
            DEVICES[protocol][device_name] = make_device_type(device_name, type_id, params)
            LOGGER.debug('Loaded device type', name=device_name, type_id=type_id)


@cachetools.cached(cache={})
def get_device_type(device_id: int = None, device_name: str = None,
                    protocol: str = 'smartsensor') -> type:
    for name, device in DEVICES[protocol].items():
        if device_id == device.type_id or name == device_name:
            return device
    raise RuntimeBaseException('Device not found', device_id=device_id, protocol=protocol)


DeviceBuffer = collections.namedtuple('DeviceBuffer', ['shm', 'struct'])


class DeviceEvent(enum.Enum):
    CONNECT = enum.auto()
    DISCONNECT = enum.auto()
    HEARTBEAT_RES = enum.auto()
    ERROR = enum.auto()


@dataclasses.dataclass
class SmartSensorProxy(collections.UserDict):
    connections: Connection
    command_publisher: Connection
    ready: asyncio.Event = dataclasses.field(default_factory=asyncio.Event, init=False)
    buffer: DeviceBuffer = dataclasses.field(default=None, init=False)

    async def ping(self):
        pass

    async def request_subscription(self):
        pass

    async def request_heartbeat(self):
        pass

    def read_soon(self, param_name: str):
        pass

    def write_soon(self, param_name: str, value):
        pass

    async def event_loop(self):
        while True:
            event = await self.event_subscriber.recv()
