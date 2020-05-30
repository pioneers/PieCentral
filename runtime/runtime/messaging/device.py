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
from runtime.util.exception import RuntimeBaseException


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
