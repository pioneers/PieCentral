"""
The device
"""

import asyncio
import collections
import ctypes
import dataclasses
import enum
from multiprocessing.shared_memory import SharedMemory
from numbers import Real
import time
from typing import Callable, Iterable, List, Union

import cachetools
import yaml
import zmq
from schema import And, Optional, Regex, Schema, Use
import structlog

from runtime.messaging.connection import Connection
from runtime.monitoring import log
from runtime.util import VALID_NAME, ParameterValue, TTLMapping
from runtime.util.exception import RuntimeBaseException


LOG_CAPTURE = log.LogCapture()
LOGGER = log.get_logger(LOG_CAPTURE)
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
            super().__setattr__(name, value)
    return TimestampedParameter


class SmartSensorUID(Structure):
    """
    A Smart Sensor Unique Identifer (UID).

    The UID is effectively a 96-bit integer that encodes Sensor metadata:
      * `device_type`: An integer denoting the type of Sensor. The types are
            given by the Smart Sensor protocol specification.
      * `year`: The year the Sensor is from. 2016 is denoted as year zero.
      * `id`: A randomly generated ID. This ensures the probability of a UID
            collision (two devices of the same type from the same year) is
            negligible.
    """
    _pack_ = 1  # Ensure the fields are byte-aligned (pack as densely as possible)
    _fields_ = [
        ('device_type', ctypes.c_uint16),
        ('year', ctypes.c_uint8),
        ('id', ctypes.c_uint64),
    ]

    def to_int(self) -> int:
        """
        Return an integer representation of this UID.

        Warning::
            Serializing the UID as an integer may fail if the serializer cannot
            represent integers larger than 64 bits (UID is 96 bits).
        """
        return (self.device_type << 72) | (self.year << 64) | self.id


def get_field_bytes(structure: ctypes.Structure, field_name: str) -> bytes:
    field_description = getattr(type(structure), field_name)
    field_ref = ctypes.byref(structure, field_description.offset)
    return ctypes.string_at(field_ref, field_description.size)


class DeviceStructure(Structure):
    """
    A device with readable/writeable parameters.

    Device structures are C-style structs dynamically created with the
    ``ctypes`` module. Every parameter consists of up to two struct fields,
    depending on whether the parameter is "readable" or "writeable". The
    "current" field of each parameter holds the authoritative value (i.e. used
    for reads), whereas the "desired" field is used to command the peripheral
    (i.e. used for writes), since peripherals usually cannot be commanded
    instantaneously.

    Note::
        We use the term "device" to refer to not just Smart Sensors, but also
        gamepads and possibly other peripherals. Devices provide a uniform
        interface for sharing peripheral state between processes.
    """
    Parameter = collections.namedtuple(
        'Parameter',
        ['name', 'type', 'lower', 'upper', 'readable', 'writeable'],
        defaults=[float('-inf'), float('inf'), True, False],
    )

    def get_current(self, param_name: str) -> ParameterValue:
        """ Get the current value of a parameter. """
        return getattr(self, f'current_{param_name}').value

    def set_current(self, param_name: str, value: ParameterValue):
        """ Set the current value of a parameter. """
        getattr(self, f'current_{param_name}').value = value

    def set_desired(self, param_name: str, value: ParameterValue):
        """ Set the desired value of a parameter. """
        getattr(self, f'desired_{param_name}').value = value

    @classmethod
    def get_parameters(cls, bitmap: int) -> Iterable[Parameter]:
        """ Translate a parameter bitmap into parameters. """
        for i in range(len(cls._params)):
            if (bitmap >> i) & 0b1:
                yield cls._params[i]

    @classmethod
    def make_type(cls: type, name: str, type_id: int, params: List[Parameter],
                  *extra_fields, base_cls: type = None) -> type:
        """
        Make a device type (C-style structure) from a parameter configuration.

        Arguments:
            name: The device name.
            type_id: A unique integer identifying the device.
            params: A list of parameters (parameters are ordered, so they can
                be referred to by either their index or name).
            extra_fields: Any other fields to include in this type.

        Returns:
            A device type (subclass of a ``ctypes.Structure``). Instances of
            this type can be constructed by wrapping writeable buffers using
            the `from_buffer` method.
        """
        fields = list(extra_fields)
        for param in params:
            ctype = make_timestamped_parameter(param.type)
            if param.readable:
                fields.append((f'current_{param.name}', ctype))
            if param.writeable:
                fields.append((f'desired_{param.name}', ctype))
        return type(name, (base_cls or cls, ), {
            '_params': params,
            '_param_ids': {param.name: index for index, param in enumerate(params)},
            '_fields_': fields,
            'type_id': type_id,
        })


class SmartSensorStructure(DeviceStructure):
    """
    A special device structure for Smart Sensors.

    Attributes:
        RESET_MAP: Used to clear the read/write map.
        MAX_PARAMETERS: The maximum number of parameter allowed by the Smart
            Sensor protocol.
    """
    RESET_MAP: int = 0x0000
    MAX_PARAMETERS: int = 16

    def set_desired(self, param_name: str, value: ParameterValue):
        super().set_desired(param_name, value)
        self.write |= 1 << self._param_ids[param_name]

    def set_current(self, param_name: str, value: ParameterValue):
        super().set_current(param_name, value)
        self.send |= 1 << self._param_ids[param_name]

    @classmethod
    def make_type(cls: type, name: str, type_id: int,
                  params: List[DeviceStructure.Parameter]) -> type:
        """
        Make a device type with extra fields to implement the Smart Sensor protocol.

        The extra fields included are:
          * `write`: A bitmap indicating which parameters should be written.
          * `read`: A bitmap indicating which parameters should be read.
          * `delay`: The current subscription period.
          * `subscription`: A bitmap of the parameters the Smart Sensor consumer
            is subscribed to.
          * `uid`: The unique identifier of the Smart Sensor.

        See ``DeviceStructure.make_type`` for a similar signature.
        """
        if len(params) > cls.MAX_PARAMETERS:
            raise RuntimeBaseException('Maxmimum number of Smart Sensor parameters exceeded')
        extra_fields = [
            ('write', ctypes.c_uint16),
            ('read', ctypes.c_uint16),
            ('send', ctypes.c_uint16),
            ('delay', ctypes.c_uint16),
            ('subscription', ctypes.c_uint16),
            ('uid', SmartSensorUID),
        ]
        return DeviceStructure.make_type(name, type_id, params, *extra_fields, base_cls=cls)


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


def load_device_types(schema: str, sensor_protocol: str = 'smartsensor'):
    """
    """
    schema = DEVICE_SCHEMA.validate(schema)
    for protocol, devices in schema.items():
        dev_configs = DEVICES.setdefault(protocol, {})
        device_type = SmartSensorStructure if protocol == sensor_protocol else DeviceStructure
        for device_name, device_conf in devices.items():
            params = [DeviceStructure.Parameter(**param_conf)
                      for param_conf in device_conf['params']]
            type_id = device_conf['id']
            dev_configs[device_name] = device_type.make_type(device_name, type_id, params)
            LOGGER.debug('Loaded device type', name=device_name, type_id=type_id)


@cachetools.cached(cache={})
def get_device_type(device_id: int = None, device_name: str = None,
                    protocol: str = None) -> type:
    """
    """
    protocols = [protocol] if protocol is not None else DEVICES.keys()
    for protocol in protocols:
        devices = DEVICES.get(protocol) or {}
        for name, device in devices.items():
            if device_id == device.type_id or name == device_name:
                return device
    raise RuntimeBaseException('Device not found', device_id=device_id, protocol=protocol)


@dataclasses.dataclass
class DeviceBuffer:
    shm: SharedMemory
    struct: DeviceStructure

    @property
    def is_smart_sensor(self):
        return isinstance(self.struct, SmartSensorStructure)

    @property
    def status(self):
        return {'device_type': type(self.struct).__name__, 'device_uid': self.shm.name}

    @classmethod
    def open(cls, device_type: type, device_uid: str, *, create=False):
        context = {'device_type': device_type.__name__, 'device_uid': device_uid}
        try:
            shm = SharedMemory(device_uid, create=create, size=ctypes.sizeof(device_type))
        except FileNotFoundError:
            LOGGER.error('Cannot attach to nonexistent shared memory block', **context)
            raise
        except FileExistsError:
            shm = SharedMemory(device_uid)
            LOGGER.warn('Shared memory block already exists', **context)
        else:
            LOGGER.debug('Opened shared memory block', create=create, **context)
        return DeviceBuffer(shm, device_type.from_buffer(shm.buf))


class DeviceEvent(enum.Enum):
    CONNECT = enum.auto()
    DISCONNECT = enum.auto()
    HEARTBEAT_RES = enum.auto()
    ERROR = enum.auto()


class DeviceMapping(TTLMapping):
    """
    """

    def __init__(self, ttl: Real, logger: None = structlog.BoundLoggerBase):
        super().__init__(ttl, self.on_device_disconnect)
        self.logger = logger or LOGGER

    async def open(self, device_uid: str, device_type: type, *, create=False):
        if device_uid in self:
            await self.keep_alive(device_uid)
        else:
            self[device_uid] = DeviceBuffer.open(device_type, device_uid, create=create)
            asyncio.create_task(self.expire(device_uid))
            self.logger.debug(
                'Opened device',
                device_uid=device_uid,
                device_type=device_type.__name__)

    def on_device_disconnect(self, device_uid: str, device_buffer: DeviceBuffer):
        del device_buffer.struct
        device_buffer.shm.close()
        self.logger.debug('Device disconnected', device_uid=device_uid)


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
