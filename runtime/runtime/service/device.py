import asyncio
import collections
import ctypes
import dataclasses
import enum
import functools
from multiprocessing.shared_memory import SharedMemory
from numbers import Real
import os
import time
from typing import Iterable, Set

import aioserial
import backoff
from pyudev import Context, Device, Monitor, MonitorObserver
from schema import Optional
from serial.serialutil import SerialException
from serial.tools import list_ports

from runtime.messaging import packet as packetlib
from runtime.messaging.device import (
    DeviceBuffer,
    SmartSensorStructure,
    SmartSensorUID,
    get_device_type,
)
from runtime.messaging.routing import Connection
from runtime.monitoring import log
from runtime.service.base import Service
from runtime.util import POSITIVE_INTEGER, POSITIVE_REAL
from runtime.util.exception import RuntimeBaseException


LOG_CAPTURE = log.LogCapture()
LOGGER = log.get_logger(LOG_CAPTURE)


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
        # We need to store the event loop of the main thread.
        self.loop = asyncio.get_running_loop()
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


@dataclasses.dataclass
class SmartSensor:
    """
    A Smart Sensor and an implementation of its initialize/read/write protocols.
    """
    serial_conn: aioserial.AioSerial
    event_queue: asyncio.Queue
    command_queue: asyncio.Queue = dataclasses.field(default_factory=asyncio.Queue)
    write_interval: Real = 0.05
    terminate_timeout: Real = 2
    ready: asyncio.Event = dataclasses.field(default_factory=asyncio.Event, init=False)
    buffer: DeviceBuffer = dataclasses.field(default=None, init=False)

    def __hash__(self):
        return hash(self.serial_conn.port)

    async def initialize_sensor(self, uid: SmartSensorUID):
        device_type = get_device_type(uid.device_type)
        device_uid = f'smart-sensor-{uid.to_int()}'
        self.buffer = DeviceBuffer.open(device_type, device_uid, create=True)
        LOGGER.info('Initialized new sensor', device_type=device_type.__name__,
                    device_uid=device_uid)

    async def handle_sub_res(self, packet):
        uid = packet.uid
        if not self.buffer:
            await self.initialize_sensor(uid)
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
            await self.handle_sub_res(packet)
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
                LOGGER.warn('Encountered a packet encoding exception', exc_info=exc)
            else:
                await self.handle_inbound_packet(packet)

    async def write_parameters_loop(self, cycle_period: int = 1000):
        await self.ready.wait()
        start, count = time.time(), 0
        while True:
            await asyncio.sleep(self.write_interval)

            # Testing
            # self.buffer.struct.write = 0xffff
            # self.buffer.struct.set_desired('duty_cycle', 0.5)
            # self.buffer.struct.set_desired('enc_pos', 20)  # Doesn't work
            # self.buffer.struct.set_desired('deadband', 1)

            if self.buffer.struct.write != SmartSensorStructure.RESET_MAP:
                packet = packetlib.make_dev_write(self.buffer.struct)
                self.buffer.struct.write = SmartSensorStructure.RESET_MAP
                await packetlib.send(self.serial_conn, packet)

            if self.buffer.struct.read != SmartSensorStructure.RESET_MAP:
                packet = packetlib.make_dev_read(self.buffer.struct)
                self.buffer.struct.read = SmartSensorStructure.RESET_MAP
                await packetlib.send(self.serial_conn, packet)

            count = (count + 1)%cycle_period
            if count == 0:
                end = time.time()
                start, frequency = end, round(cycle_period/(end - start), 3)
                LOGGER.debug('Estimated parameter write frequency',
                             frequency=frequency, uid=self.buffer.struct.uid.to_int())

    async def write_commands_loop(self):
        pass

    @backoff.on_exception(backoff.constant, asyncio.TimeoutError, max_tries=10, logger=LOGGER)
    async def ping(self, timeout: Real = 1):
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

    @backoff.on_exception(backoff.constant, BufferError, max_tries=5, interval=1, logger=LOGGER)
    async def terminate(self, shm: SharedMemory):
        shm.close()
        shm.unlink()
        LOGGER.info('Smart sensor terminated', device_uid=shm.name)

    async def spin(self):
        """ Run this sensor indefinitely. """
        try:
            await asyncio.gather(
                self.ping(),
                self.read_loop(),
                self.write_parameters_loop(),
                self.write_commands_loop(),
            )
        except SerialException as exc:
            LOGGER.error('Serial exception, closing Smart Sensor', exc_info=exc)
        finally:
            if self.buffer:
                shm = self.buffer.shm
                # NOTE: `shm.close` can fail sometimes because the ctype struct
                # maintains a pointer to the buffer. We need to trigger the
                # garbage collection of the struct.
                del self.buffer
                await asyncio.sleep(self.terminate_timeout)
                await self.terminate(shm)


@dataclasses.dataclass
class DeviceService(Service):
    sensors: Set = dataclasses.field(default_factory=set)
    event_queue: asyncio.Queue = dataclasses.field(default_factory=asyncio.Queue)

    config_schema = {
        **Service.config_schema,
        Optional('baud_rate', default=115200): POSITIVE_INTEGER,
        Optional('max_hotplug_events', default=128): POSITIVE_INTEGER,
        Optional('broadcast_interval', default=0.2): POSITIVE_REAL,
        Optional('write_interval', default=0.05): POSITIVE_REAL,
        Optional('terminate_timeout', default=2): POSITIVE_REAL,
    }

    def initialize_hotplugging(self):
        """
        Connect all existing sensors and start a thread to detect future hotplug events.

        Returns::
            asyncio.Queue: A queue to hold hotplug events.
        """
        event_queue = asyncio.Queue(self.config['max_hotplug_events'])
        observer = SmartSensorObserver(event_queue)
        observer.handle_initial_sensors()
        observer.start()
        return event_queue

    async def open_serial_connections(self, hotplug_event, **serial_options):
        """ Open a serial connection to a new sensor and schedule its read/write loops. """
        for port in hotplug_event.ports:
            serial_conn = aioserial.AioSerial(port, **serial_options)
            serial_conn.rts = False
            sensor = SmartSensor(
                serial_conn,
                self.event_queue,
                write_interval=self.config['write_interval'],
                terminate_timeout=self.config['terminate_timeout'],
            )
            self.sensors.add(sensor)
            sensor_task = asyncio.create_task(sensor.spin())
            sensor_task.add_done_callback(functools.partial(self.sensors.remove, sensor))

    async def broadcast_status(self):
        """ Periodically notify all other services about currently available sensors. """
        with Connection.open(self.config['sockets']['sensor_status']) as connection:
            while True:
                devices = [sensor.buffer.status for sensor in self.sensors if sensor.buffer]
                await connection.send({'devices': devices})
                await asyncio.sleep(self.config['broadcast_interval'])

    async def main(self):
        LOG_CAPTURE.connect(self.log_records)
        asyncio.create_task(self.broadcast_status())
        event_queue = self.initialize_hotplugging()
        while True:
            hotplug_event = await event_queue.get()
            if hotplug_event.action is HotplugAction.ADD:
                await self.open_serial_connections(hotplug_event, baudrate=self.config['baud_rate'])
