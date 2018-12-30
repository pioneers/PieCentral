"""
This module manages Smart Sensor communication.
"""


__all__ = ['SmartSensorObserver']

import asyncio
import collections
import functools
from numbers import Real
from typing import List, Callable, Generator, Sequence
import ctypes
import os
import socket
import serial
import serial_asyncio
import struct
import time
import threading

from serial.tools.list_ports import comports
import yaml

from runtime.buffer import MAX_PARAMETERS, BinaryRingBuffer, SensorReadBuffer, SensorWriteBuffer
import runtime.journal
from runtime.messaging import Circuitbreaker
from runtime import packet as packet_lib
from runtime.util import RuntimeBaseException, read_conf_file

LOGGER = runtime.journal.make_logger(__name__)

try:
    from pyudev import Context, Devices, Device, Monitor, MonitorObserver
    udev_enabled = True
except ImportError:
    LOGGER.warning('Unable to import `pyudev`, which is Linux-only.')
    udev_enabled = False


Parameter = collections.namedtuple(
    'Parameter',
    ['name', 'type', 'lower', 'upper', 'readable', 'writeable'],
    defaults=[float('-inf'), float('inf'), True, False],
)


class SensorService(collections.UserDict):
    def __init__(self, schema_filename, dependents: set = None):
        self.dependents = {Circuitbreaker(path=path) for path in (dependents or {})}
        self.access, self.sensor_types = asyncio.Lock(), {}
        schema = read_conf_file(schema_filename)
        for dev_id, read_type, write_type in self.parse_schema(schema):
            self.sensor_types[dev_id] = read_type, write_type
        super().__init__()

    @staticmethod
    def parse_schema(schema):
        for _, devices in schema.items():
            for dev_name, device in devices.items():
                params = []
                for descriptor in device.get('params', ()):
                    attrs = {
                        'name': descriptor['name'],
                        'type': getattr(ctypes, f'c_{descriptor["type"]}'),
                    }
                    for attr in Parameter._fields[2:]:
                        if attr in descriptor:
                            attrs[attr] = descriptor[attr]
                    params.append(Parameter(**attrs))

                dev_id = device['id']
                yield (
                    dev_id,
                    SensorReadStructure.make_type(dev_name, dev_id, params),
                    SensorWriteStructure.make_type(dev_name, dev_id, params),
                )

    async def register(self, uid: str):
        async with self.access:
            LOGGER.debug('Registered device.', uid=uid)
            for dependent in self.dependents:
                await dependent.register_device(uid)

    async def unregister(self, uid: str):
        async with self.access:
            LOGGER.debug('Unregistered device.', uid=uid)
            for dependent in self.dependents:
                await dependent.unregister_device(uid)

    async def write(self, uid: str, params):
        """ Issues a write command. """

    async def read(self, uid: str, params):
        """ Issues a read command. """

    async def collect(self, uid: str):
        pass

    def get_read_type(self, dev_id: int) -> type:
        read_type, _ = self.sensor_types[dev_id]
        return read_type

    def get_write_type(self, dev_id: int) -> type:
        _, write_type = self.sensor_types[dev_id]
        return write_type

    @staticmethod
    def get_read_buf_name(uid: int) -> str:
        return f'sensor-rbuf-{uid}'

    @staticmethod
    def get_write_buf_name(uid: int) -> str:
        return f'sensor-wbuf-{uid}'


class SensorObserver(MonitorObserver):
    subsystem, device_type = 'usb', 'usb_interface'

    def __init__(self, sensor_service: SensorService, baud_rate: int, thread_name: str = 'device-observer'):
        self.loop = asyncio.get_event_loop()
        self.sensor_service, self.baud_rate = sensor_service, baud_rate
        self.thread_name, self.context = thread_name, Context()
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(self.subsystem, self.device_type)
        super().__init__(self.monitor, self.handle_hotplug_event, name=self.thread_name)

    def list_devices(self) -> Generator[Device, None, None]:
        for device in self.context.list_devices(subsystem=self.subsystem):
            if self.is_sensor(device):
                yield device

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

    def open_serial_conn(self, com_port: str):
        """ Create a serial connection and add it to the running event loop. """
        LOGGER.debug('Creating serial connection.', com_port=com_port, baud_rate=self.baud_rate)
        make_protocol = lambda: SensorProtocol(self.sensor_service)
        conn = serial_asyncio.create_serial_connection(self.loop, make_protocol,
                                                       com_port, baudrate=self.baud_rate)
        asyncio.ensure_future(conn, loop=self.loop)

    def handle_hotplug_event(self, action, device):
        path, product = device.sys_path, device.properties.get('PRODUCT')
        if self.is_sensor(device):
            if action.lower() == 'add':
                for com_port in self.get_com_ports({device}):
                    self.open_serial_conn(com_port)
                return
            elif action.lower() == 'remove':
                return
        LOGGER.debug('Ignoring irrelevant hotplug event.',
                     action=action, path=path, product=product)

    def load_initial_sensors(self):
        for com_port in self.get_com_ports(self.list_devices()):
            self.open_serial_conn(com_port)


class SensorProtocol(asyncio.Protocol):
    """
    An implementation of the Smart Sensor protocol.

    Attributes:
        read_buf (BinaryRingBuffer): Holds COBS-encoded packets just read.
        write_buf (BinaryRingBuffer): Holds COBS-encoded packets ready to be written.
    """
    def __init__(self, sensor_service):
        self.sensor_service = sensor_service
        self.read_queue, self.write_queue = BinaryRingBuffer(), BinaryRingBuffer()
        # self.encoder = threading.Thread(
        #     target=packet.encode_loop,
        #     args=(),
        # )

        self.send_count, self.recv_count = 0, 0
        self.ready = asyncio.Event()
        self.read_timeout, self.write_timeout = 1, 10

    def connection_made(self, transport):
        self.transport = transport
        transport.serial.rts = False
        LOGGER.debug('Connection made to serial.', com_port=transport.serial.port)

        loop = asyncio.get_event_loop()
        self.log_task = asyncio.create_task(self.log_statistics())
        self.send_task = asyncio.ensure_future(loop.run_in_executor(None, self.send_messages))
        self.ping_task = asyncio.create_task(self.ping())

    @property
    def port(self):
        return self.transport.serial.port

    async def ping(self, delay=0.5):
        try:
            while not self.ready.is_set():
                packet_lib.append_packet(self.write_queue, packet_lib.make_ping())
                await asyncio.sleep(delay)
                LOGGER.debug('Sending ping.')
        except asyncio.CancelledError:
            pass
        finally:
            LOGGER.debug('Handshake completed. Stopping ping.')

    def connection_lost(self, exc):
        LOGGER.debug('Connection to serial lost.', com_port=self.port)
        self.send_task.cancel()
        self.log_task.cancel()
        self.ready.clear()
        self.read_queue.clear()
        self.write_queue.clear()

    def make_sensor(self, dev_id, uid, read=True):
        if read:
            name = self.sensor_service.get_read_buf_name(uid)
            struct_type = self.sensor_service.get_read_type(dev_id)
            sensor_buf = SensorReadBuffer(name, struct_type)
        else:
            name = self.sensor_service.get_write_buf_name(uid)
            struct_type = self.sensor_service.get_write_type(dev_id)
            sensor_buf = SensorWriteBuffer(name, struct_type)
            LOGGER.debug(repr(sensor_buf))
        LOGGER.debug('Building sensor structure.',
                     read=read,
                     name=name,
                     struct_type=struct_type.__name__)
        return struct_type.from_buffer(sensor_buf), sensor_buf

    def data_received(self, data: bytes):
        self.recv_count += 1
        self.read_queue.extend(data)
        if not self.ready.is_set():
            packet = self.read_queue.read_with_timeout(self.read_timeout)
            if not packet:
                return
            packet = packet_lib.extract_from_frame(packet)
            if not packet:
                LOGGER.error('Unable to extract packet from COBS frame.')
                return
            (msg_type, payload_len), payload = packet[:2], packet[2:]
            msg_type = packet_lib.MessageType(msg_type)
            if msg_type is not packet_lib.MessageType.SUB_RES:
                LOGGER.debug('Subscription response not received during handshake.', msg_type=msg_type.name)
            elif payload_len != len(payload) or payload_len != 15:
                LOGGER.error('Subscription response payload length not correct.')
            else:
                params, delay, dev_id, year, rand_id = struct.unpack('<HHHBQ', payload)
                uid = dev_id << 72 | year << 64 | rand_id

                self.read_struct, self.read_buf = self.make_sensor(dev_id, uid)
                self.write_struct, self.write_buf = self.make_sensor(dev_id, uid, read=False)
                LOGGER.info('Sensor registered.', uid=uid, dev_id=dev_id)
                self.ready.set()

    async def log_statistics(self):
        try:
            while True:
                await asyncio.sleep(5)
                LOGGER.debug('Device statistics.', recv_count=self.recv_count)
        except asyncio.CancelledError:
            LOGGER.debug('Stopping log task.')

    def send_messages(self):
        LOGGER.debug('Sending messages to device.')
        while not self.transport.is_closing():
            packet = self.write_queue.read_with_timeout(self.write_timeout)
            if not packet:
                LOGGER.warn('Write queue read timed out.',
                            write_timeout=self.write_timeout,
                            com_port=self.port)
            LOGGER.critical(repr(packet))
            self.transport.write(b'\x00' + packet)


class SensorStructure(ctypes.LittleEndianStructure):
    """
    A struct representing a device (for example, a Smart Sensor).

    Example:

        >>> YogiBear = DeviceStructure.make_device_type('YogiBear',
        ...     [Parameter('duty_cycle', ctypes.c_float, -1, 1)])
        >>> motor = multiprocessing.Value(YogiBear, lock=False)
        >>> start = time.time()
        >>> motor.duty_cycle = -0.9
        >>> motor.last_modified('duty_cycle') - start < 0.1  # Updated recently?
        True
        >>> motor.duty_cycle = -1.1
        Traceback (most recent call last):
          ...
        ValueError: Assigned invalid value -1.1 to "YogiBear.duty_cycle" (not in bounds).
    """
    register_type = ctypes.c_uint64

    @staticmethod
    def _get_timestamp_name(param_name: str) -> str:
        return param_name + '_ts'

    def last_modified(self, param_name: str) -> float:
        return getattr(self, self._get_timestamp_name(param_name))

    def __setattr__(self, param_name: str, value):
        """ Validate and assign the parameter's value, and update its timestamp. """
        if isinstance(value, Real):
            param = self._params[param_name]
            if not param.lower <= value <= param.upper:
                cls_name = self.__class__.__name__
                raise ValueError(f'Assigned invalid value {value} to '
                                 f'"{cls_name}.{param_name}" (not in bounds).')
        super().__setattr__(self._get_timestamp_name(param_name), time.time())
        super().__setattr__(param_name, value)

    def __getitem__(self, param_id):
        return self.__class__._params_by_id[param_id]

    @classmethod
    def make_type(cls, dev_name: str, dev_id: int, params: List[Parameter], *extra_fields) -> type:
        if len(params) > MAX_PARAMETERS:
            LOGGER.warning(
                'Device has too many parameters.',
                max_params=MAX_PARAMETERS,
                device=dev_name,
            )

        fields = list(extra_fields) or []
        for param in params:
            fields.extend([
                (param.name, param.type),
                (cls._get_timestamp_name(param.name), ctypes.c_double),
            ])

        return type(dev_name, (cls,), {
            '_dev_id': dev_id,
            '_fields_': fields,
            '_params': {param.name: param for param in params},
            '_params_by_id': params,
        })


class SensorReadStructure(SensorStructure):
    base_year = 2016  # Spring

    @property
    def uid(self):
        return self.dev_type << 72 | self.year_offset << 64 | self.id

    @property
    def year(self):
        return self.base_year + self.year_offset

    @classmethod
    def make_type(cls, dev_name: str, dev_id: int, params: List[Parameter]) -> type:
        return SensorStructure.make_type(
            dev_name.capitalize() + 'ReadStructure',
            dev_id,
            [param for param in params if param.readable],
            ('dev_type', ctypes.c_uint16),
            ('year_offset', ctypes.c_uint8),
            ('id', ctypes.c_uint64),
            ('delay', cls.register_type),
            ('sub_params', cls.register_type),
            ('heartbeat_id', ctypes.c_uint8),
            ('error_code', ctypes.c_uint8),
            ('sub_res_present', ctypes.c_bool),
            ('heartbeat_res_present', ctypes.c_bool),
            ('error_present', ctypes.c_bool),
        )


class SensorWriteStructure(SensorStructure):
    @classmethod
    def make_type(cls, dev_name: str, dev_id: int, params: List[Parameter]) -> type:
        return SensorStructure.make_type(
            dev_name.capitalize() + 'WriteStructure',
            dev_id,
            [param for param in params if param.writeable],
            ('write_flags', cls.register_type),
            ('read_flags', cls.register_type),
        )


def initialize_hotplugging(service, options):
    if options['poll'] or not udev_enabled:
        raise NotImplementedError('Polling-based hotplugging has not yet been implemented.')
    else:
        observer = SensorObserver(service, options['baud_rate'])
        observer.start()
        observer.load_initial_sensors()
        return observer


async def log_statistics(period):
    while True:
        LOGGER.debug('Device statistics.')
        await asyncio.sleep(period)


async def start(options):
    service = SensorService(options['dev_schema'], {options['exec_srv'], options['net_srv']})
    LOGGER.debug('Loaded sensor schemas.')
    observer = initialize_hotplugging(service, options)
    client = Circuitbreaker(host=options['host'], port=options['tcp'])
    try:
        await log_statistics(options['stat_period'])
    except asyncio.CancelledError:
        observer.stop()
