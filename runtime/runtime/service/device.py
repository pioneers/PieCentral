import asyncio
import collections
import ctypes
import dataclasses
from multiprocessing.shared_memory import SharedMemory
from numbers import Real
import os
import time
from typing import List

import aiofiles
# TODO: poll for cross-platform
from pyudev import Context, Devices, Device, Monitor, MonitorObserver
from schema import Schema, And, Use, Optional
import yaml

from runtime.service.base import Service
from runtime.util import get_module_path
from runtime.util.exception import EmergencyStopException, RuntimeBaseException


class DeviceProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        pass

    def connection_lost(self, exc):
        pass

    def data_received(self, data):
        pass

    def eof_received(self):
        pass


class DeviceStructure(ctypes.LittleEndianStructure):
    """
    A struct representing a device (for example, a Smart Sensor).
    """
    Parameter = collections.namedtuple(
        'Parameter',
        ['name', 'type', 'lower', 'upper', 'readable', 'writeable'],
        defaults=[float('-inf'), float('inf'), True, False],
    )
    timestamp_type = ctypes.c_double

    @staticmethod
    def _get_timestamp_name(param_name: str) -> str:
        return f'{param_name}_ts'

    @staticmethod
    def _get_time() -> Real:
        return time.time()

    def last_modified(self, param_name: str) -> Real:
        return getattr(self, self._get_timestamp_name(param_name))

    def __setattr__(self, param_name: str, value):
        """ Validate and assign a parameter value, and update its timestamp. """
        param = self._params[param_name]
        if isinstance(value, Real):
            if not param.lower <= value <= param.upper:
                raise RuntimeBaseException(
                    'Invalid value assigned to device parameter',
                    cause='invalid-bounds',
                    value=value,
                    lower=param.lower,
                    upper=param.upper,
                    param_name=param.name,
                    dev_name=self.__class__.__name__,
                )
        super().__setattr__(self._get_timestamp_name(param_name), self._get_time())
        super().__setattr__(param_name, value)

    @classmethod
    def make_type(cls: type, name: str, type_id: int, params: List[Parameter], *extra_fields) -> type:
        """
        Create a new device structure type using subclassing.

        Arguments:
            name: The name of the device.
            type_id: The unique device type identifier, as outlined in the Smart Sensors spec.
            params: A list of device parameters.
            extra_fields: Auxiliary fields (not Smart Sensor parameters).
        """
        fields = list(extra_fields)
        for param in params:
            fields.extend([
                (param.name, param.type),
                (cls._get_timestamp_name(name), cls.timestamp_type),
            ])

        return type(name, (cls, ), {
            '_params': {param.name: param for param in params},
            '_fields_': fields,
            'type_id': type_id,
        })


DEVICES_SCHEMA = Schema(And(Use(dict), {
    str: And(Use(dict), {
        str: And(Use(dict), {
            'id': And(Use(int), lambda type_id: 0 <= type_id < 0xffff),
            'params': And(Use(list),
                [And(Use(dict), {
                    'name': Use(str),
                    'type': And(Use(str), Use(lambda dev_type: getattr(ctypes, f'c_{dev_type}'))),
                    Optional('lower'): Use(float),
                    Optional('upper'): Use(float),
                    Optional('readable'): Use(bool),
                    Optional('writeable'): Use(bool),
                })],
            ),
        }),
    }),
}), ignore_extra_keys=True)


async def get_device_schema(schema_path: str):
    async with aiofiles.open(schema_path) as schema_file:
        device_schema = yaml.load(await schema_file.read())
    device_schema = DEVICES_SCHEMA.validate(device_schema)
    device_types = {}
    for protocol, devices in device_schema.items():
        for device, config in devices.items():
            device_types[device] = DeviceStructure.make_type(device, config['id'], [
                DeviceStructure.Parameter(**param) for param in config['params']
            ])
    return device_types


@dataclasses.dataclass
class DeviceService(Service):
    async def main(self, config):
        # print(await get_device_schema(get_module_path(self.config['variables']['device_schema'])))

        # YogiBear = DeviceStructure.make_type('YogiBear', 0xA, [DeviceStructure.Parameter('duty_cycle', ctypes.c_float, -1, 1)])
        # while True:
        #     y = YogiBear()
        #     self.logger.debug('OK!', s=ctypes.sizeof(y))
        #     y.duty_cycle = 2
        #     await asyncio.sleep(1)

        # self.logger.debug('Config', config=device_schema)

        # while True:
        #     self.logger.debug('Sending ping to journal.')
        #     await self.raw_sockets['journal'].send(b'ping')
        #     await asyncio.sleep(1)

        while True:
            self.logger.debug('Hello!')
            await asyncio.sleep(1)
