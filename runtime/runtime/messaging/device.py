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
import typing

import backoff
import cachetools
import yaml
import zmq
from schema import And, Optional, Regex, Schema, Use
import structlog

from runtime.messaging import packet as packetlib
from runtime.messaging.connection import Connection
from runtime.monitoring import log
from runtime.util import VALID_NAME, ParameterValue, TTLMapping
from runtime.util.exception import RuntimeBaseException


LOG_CAPTURE = log.LogCapture()
LOGGER = log.get_logger(LOG_CAPTURE)


@cachetools.cached(cache={})
def make_timestamped_parameter(param_type) -> type:
    class TimestampedParameter(packetlib.Structure):
        _fields_ = [
            ('value', param_type),
            ('last_updated', ctypes.c_double),
        ]

        def __setattr__(self, name: str, value):
            if name == 'value':
                self.last_updated = time.time()
            super().__setattr__(name, value)
    return TimestampedParameter


class DeviceStructure(packetlib.Structure):
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
        ['name', 'type', 'lower', 'upper', 'readable', 'writeable', 'subscribed'],
        defaults=[float('-inf'), float('inf'), True, False, False],
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
    def get_parameters(cls, bitmap: int) -> typing.Iterable[Parameter]:
        """ Translate a parameter bitmap into parameters. """
        for i in range(len(cls._params)):
            if (bitmap >> i) & 0b1:
                yield cls._params[i]

    @classmethod
    def make_type(cls: type, name: str, type_id: int, params: typing.List[Parameter],
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

    def make_read(self) -> typing.Optional[packetlib.Packet]:
        if self.read != SmartSensorStructure.RESET_MAP:
            packet = packetlib.make_dev_read(self)
            self.read = SmartSensorStructure.RESET_MAP
            return packet

    def make_write(self) -> typing.Optional[packetlib.Packet]:
        if self.write != SmartSensorStructure.RESET_MAP:
            packet = packetlib.make_dev_write(self)
            self.write = SmartSensorStructure.RESET_MAP
            return packet

    @classmethod
    def make_subscription(cls) -> int:
        params = 0
        for i in range(len(cls._params)):
            if cls._params[i].subscribed:
                params |= 1 << i
        return params

    def get_update(self):
        update = {
            'type': type(self).__name__,
            'params': {param.name: self.get_current(param.name)
                       for param in self.get_parameters(self.send)}
        }
        self.send = SmartSensorStructure.RESET_MAP
        return self.uid.to_int(), update

    def reset(self):
        self.read = self.write = self.send = SmartSensorStructure.RESET_MAP

    @classmethod
    def make_type(cls: type, name: str, type_id: int,
                  params: typing.List[DeviceStructure.Parameter]) -> type:
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
            ('uid', packetlib.SmartSensorUID),
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
                Optional('subscribed'): Use(bool),
            }]
        }
    }
})
DEVICES = {}


def load_device_types(schema: dict, sensor_protocol: str = 'smartsensor'):
    """
    Populate the device type registry.
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
    Get a device type from its integer identifier, name, or protocol.
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
    struct: typing.Optional[DeviceStructure]
    create: bool = False
    closing: bool = dataclasses.field(default=False, init=False)

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
        except FileNotFoundError as exc:
            raise RuntimeBaseException('Cannot attach to nonexistent shared memory block',
                                       **context) from exc
        except FileExistsError:
            shm = SharedMemory(device_uid)
            LOGGER.warn('Shared memory block already exists', **context)
        else:
            LOGGER.debug('Opened shared memory block', create=create, **context)
        return DeviceBuffer(shm, device_type.from_buffer(shm.buf), create=create)

    @backoff.on_exception(backoff.constant, BufferError, max_tries=5, interval=1, logger=LOGGER)
    async def close(self, timeout: Real = 0):
        # NOTE: `shm.close` can fail sometimes because the ctype struct
        # maintains a pointer to the buffer. We need to trigger the
        # garbage collection of the struct.
        del self.struct
        self.closing = True
        await asyncio.sleep(timeout)
        self.shm.close()
        if self.create:
            self.shm.unlink()
        LOGGER.debug('Closed device buffer')


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
        asyncio.create_task(device_buffer.close())
        self.logger.info('Device terminated', device_uid=device_uid)


class DeviceEvent(enum.Enum):
    UPDATE = enum.auto()


class SmartSensorCommand(enum.Enum):
    PING_ALL = enum.auto()
    DISABLE_ALL = enum.auto()
    REQ_SUB = enum.auto()
    REQ_HEART = enum.auto()
    RTT = enum.auto()
