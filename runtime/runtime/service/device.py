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


class SmartSensorProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        pass

    def data_received(self, data):
        pass

    def eof_received(self):
        pass


class SmartSensorObserver(MonitorObserver):
    def __init__(self, baud_rate: int, name: str = 'device-observer',
                 subsystem: str = 'usb', device_type: str = 'usb_interface'):
        self.context = Context()
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem, device_type)
        super().__init__(self.monitor, self.handle_hotplug_event, name=name)

    def handle_hotplug_event(self, action, device):
        path, product = device.sys_path, device.properties.get('PRODUCT')
        if SmartSensorObserver.is_sensor(device):
            if action.lower() == 'add':
                for com_port in self.get_com_ports({device}):
                    self.open_serial_conn(com_port)
                return
            elif action.lower() == 'remove':
                return
        logger.debug('Ignoring irrelevant hotplug event', action=action,
                     path=path, product=product)

    @staticmethod
    def is_sensor(device: Device) -> bool:
        """
        Determine whether the USB descriptor belongs to an Arduino Micro (CDC ACM).
        .. _Linux USB Project ID List
            http://www.linux-usb.org/usb.ids
        """
        try:
            vendor_id, product_id, _ = device.properties['PRODUCT'].split('/')
            return int(vendor_id, 16) == 0x2341 and int(product_id, 16) == 0x8037
        except (KeyError, ValueError):
            return False

    @staticmethod
    def get_com_ports(devices: Sequence[Device]):
        """ Translate a sequence of `pyudev` devices into usable COM ports. """
        ports = serial.tools.list_ports.comports(include_links=True)
        port_devices = {port.location: port.device for port in ports}
        for device in devices:
            for filename in os.listdir(device.sys_path):
                if filename.startswith('tty'):
                    for port in ports:
                        if port.location in device.sys_path:
                            yield port.device
                            break


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

        while True:
            self.logger.debug('Devices firing')
            await asyncio.sleep(20)
