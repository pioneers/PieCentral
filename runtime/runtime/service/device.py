import asyncio
import collections
import ctypes
import dataclasses
import enum
import functools
from multiprocessing.shared_memory import SharedMemory
from numbers import Real
import os
import operator
import time
from typing import List, Iterable, Mapping, Tuple

import aioserial
from pyudev import Context, Devices, Device, Monitor, MonitorObserver
from schema import Schema, And, Use, Optional
from serial.serialutil import SerialException
from serial.tools import list_ports
import structlog
import yaml

from runtime.messaging import packet as packetlib
from runtime.messaging.routing import Connection
from runtime.messaging.device import (
    DeviceBuffer,
    DeviceStructure,
    SmartSensorUID,
    get_smart_sensor_type,
)
from runtime.service.base import Service
from runtime.util.exception import EmergencyStopException, RuntimeBaseException

LOGGER = structlog.get_logger()


def is_smart_sensor(device: Device) -> bool:
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


def get_com_ports(devices: Iterable[Device]) -> Iterable[str]:
    """ Translate a sequence of udev devices into COM ports. """
    ports = list_ports.comports(include_links=True)
    for device in devices:
        for filename in os.listdir(device.sys_path):
            if filename.startswith('tty'):
                for port in ports:
                    if port.location in device.sys_path:
                        yield port.device
                        break


class HotplugAction(enum.Enum):
    ADD = enum.auto()
    REMOVE = enum.auto()
    BIND = enum.auto()
    UNBIND = enum.auto()


HotplugEvent = collections.namedtuple('HotplugEvent', ['action', 'device_path', 'ports'])


class SmartSensorObserver(MonitorObserver):
    """
    A background thread for monitoring low-level USB events asynchronously
    using `udev`.

    Event data related to smart sensors are put into a queue for consumption by
    the main thread.
    """
    def __init__(self, hotplug_queue: asyncio.Queue, name: str = 'smart-sensor-observer',
                 subsystem: str = 'usb', device_type: str = 'usb_interface'):
        self.hotplug_queue = hotplug_queue
        self.subsystem, self.device_type = subsystem, device_type
        # We need to store the event loop of the main thread, since `get_event_loop`
        # will create a new event loop if called from the background thread.
        self.loop = asyncio.get_event_loop()
        self.context = Context()
        monitor = Monitor.from_netlink(self.context)
        monitor.filter_by(subsystem, device_type)
        super().__init__(monitor, self.handle_hotplug_event, name=name)

    def handle_initial_sensors(self):
        """ Simulate `udev` ADD/BIND events for all sensors that are already plugged in. """
        for device in self.context.list_devices(subsystem=self.subsystem):
            self.handle_hotplug_event(HotplugAction.ADD.name.lower(), device)
            self.handle_hotplug_event(HotplugAction.BIND.name.lower(), device)

    def handle_hotplug_event(self, action, device):
        event = HotplugEvent(HotplugAction[action.upper()], device.device_path, [])
        if is_smart_sensor(device):
            if event.action is HotplugAction.ADD:
                event.ports.extend(get_com_ports({device}))
            self.loop.call_soon_threadsafe(self.hotplug_queue.put_nowait, event)


def initialize_hotplugging(max_size=0):
    event_queue = asyncio.Queue(maxsize=max_size)
    observer = SmartSensorObserver(event_queue)
    observer.handle_initial_sensors()
    observer.start()
    return event_queue


class SmartSensorEvent(enum.Enum):
    READY = enum.auto()
    HEARTBEAT_RES = enum.auto()
    ERROR = enum.auto()
    CLOSING = enum.auto()


@dataclasses.dataclass
class SmartSensor:
    """
    A Smart Sensor and an implementation of its initialize/read/write protocols.
    """
    serial_conn: aioserial.AioSerial
    event_publisher: Connection
    command_subscriber: Connection
    write_interval: Real = 0.02
    ready: asyncio.Event = dataclasses.field(default_factory=asyncio.Event, init=False)
    buffer: DeviceBuffer = None

    def handle_sub_res(self, packet):
        uid = packet.uid
        if not self.buffer:
            device_name, device_type = get_smart_sensor_type(uid.device_type)
            shm = SharedMemory(f'smart-sensor-{uid}', create=True, size=ctypes.sizeof(device_type))
            self.buffer = DeviceBuffer(shm, device_type.from_buffer(shm.buf))
            LOGGER.debug('Initialized device buffer', uid=uid.to_int(), device_name=device_name)
        self.ready.set()

        buf = self.buffer.struct
        buf.subscription, buf.delay = packet.parameter_map, packet.delay
        buf.uid.year, buf.uid.device_type, buf.uid.id = uid.year, uid.device_type, uid.id
        LOGGER.debug('Received subscription request', year=uid.year,
                     device_type=uid.device_type, delay=buf.delay,
                     subscription=[param.name for param in buf.get_parameters(buf.subscription)])

    async def handle_dev_data(self, packet):
        offset, param_buf = 0, memoryview(bytearray(packet.payload[2:]))
        await self.ready.wait()
        for param in self.buffer.struct.get_parameters(packet.parameter_map):
            size = ctypes.sizeof(param.type)
            value = param.type.from_buffer(param_buf[offset : offset+size])
            self.buffer.struct.set_current(param.name, value)
            offset += size
        if offset != len(param_buf):
            raise RuntimeBaseException('DEV_DATA payload contains extra data')

    async def handle_inbound_packet(self, packet):
        if packet.message_id == packetlib.MessageType.HEARTBEAT_REQ:
            response = packetlib.make_heartbeat_res(packet.heartbeat_id)
            await packetlib.send(self.serial_conn, response)
            # LOGGER.debug('Received heartbeat request and sent response',
            #              heartbeat_id=response.heartbeat_id)
        elif packet.message_id == packetlib.MessageType.HEARTBEAT_RES:
            pass
        elif packet.message_id == packetlib.MessageType.DEV_DATA:
            await self.handle_dev_data(packet)
        elif packet.message_id == packetlib.MessageType.SUB_RES:
            self.handle_sub_res(packet)
        elif packet.message_id == packetlib.MessageType.ERROR:
            pass
        else:
            raise RuntimeBaseException('Packet with bad message ID',
                                       message_id=packet.message_id)

    async def read_loop(self):
        while True:
            try:
                packet = await packetlib.recv(self.serial_conn)
            except packetlib.PacketEncodingException as exc:
                LOGGER.warn(str(exc))
            else:
                await self.handle_inbound_packet(packet)

    async def write_parameters_loop(self, cycle_period: int = 1000):
        await self.ready.wait()
        start, count = time.time(), 0
        while True:
            await asyncio.sleep(self.write_interval)

            # Testing
            self.buffer.struct.dirty = 0xffff
            self.buffer.struct.set_desired('duty_cycle', 0.1)
            self.buffer.struct.set_desired('enc_pos', 20)  # Doesn't work
            self.buffer.struct.set_desired('deadband', 1)

            if self.buffer.struct.dirty == DeviceStructure.SMART_SENSOR_CLEAN:
                continue
            packet = packetlib.make_dev_write(self.buffer.struct)
            self.buffer.struct.dirty = DeviceStructure.SMART_SENSOR_CLEAN
            await packetlib.send(self.serial_conn, packet)

            count = (count + 1)%cycle_period
            if count == 0:
                end = time.time()
                start, frequency = end, round(cycle_period/(end - start), 3)
                LOGGER.debug('Estimated parameter write frequency',
                             frequency=frequency, uid=self.buffer.struct.uid.to_int())

    async def write_commands_loop(self):
        while True:
            command = await self.command_subscriber.recv()
            print(command)

    async def write_loop(self):
        await asyncio.gather(self.write_parameters_loop(), self.write_commands_loop())

    async def initialize_sensor(self, timeout: Real = 10):
        """
        Initialize this sensor's data structures and notify all proxies.

         1. The device service pings the sensor to induce a subscription
            response, which contains type and year information.
         2. The device service identifies the structure from the `DEVICES`
            registry.
         3. The device service uses the structure to allocate a shared memory
            block of sufficient size. The device service will be responsible
            for cleaning up this block on disconnect or Runtime exit.
         4. The device service notifies all other services that a new sensor
            has been detected, prompting them to attach to the shared memory
            block. For example, this allows the sensor to be available to
            student code.

        Raises::
            asyncio.TimeoutError: Device never responded with a subscription request.
        """
        LOGGER.debug('Pinging new device', timeout=timeout)
        await packetlib.send(self.serial_conn, packetlib.make_ping())
        # Block until the subscription request arrives.
        await asyncio.wait_for(self.ready.wait(), timeout)

        # await asyncio.sleep(10)
        # await packetlib.send(self.serial_conn, packetlib.make_dev_)

    async def spin(self):
        """ Run this sensor indefinitely. """
        try:
            await asyncio.gather(self.initialize_sensor(), self.read_loop(), self.write_loop())
        except SerialException as exc:
            LOGGER.warn('Serial exception, closing Smart Sensor', message=str(exc))
        except Exception as exc:  # FIXME: remove after debugging
            import traceback
            traceback.print_exc()
        finally:
            if self.buffer:
                self.buffer.shm.unlink()
                LOGGER.debug('Unlinked device buffer', name=self.buffer.shm.name)


@dataclasses.dataclass
class DeviceService(Service):
    async def open_serial_connections(self, hotplug_event, **serial_options):
        for port in hotplug_event.ports:
            serial_conn = aioserial.AioSerial(port, **serial_options)
            serial_conn.rts = False
            asyncio.create_task(SmartSensor(
                serial_conn,
                self.connections['device_event'],
                self.connections['device_command'],
            ).spin())

    async def main(self, config):
        event_queue = initialize_hotplugging(config.get('hotplug_max_events', 0))
        while True:
            hotplug_event = await event_queue.get()
            if hotplug_event.action is HotplugAction.ADD:
                await self.open_serial_connections(hotplug_event, baudrate=config['baud_rate'])
