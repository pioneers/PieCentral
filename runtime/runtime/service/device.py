# import ctypes
import asyncio
import collections
import dataclasses
import enum
import functools
from numbers import Real
import pathlib
import random
import time
import typing

import aiozmq.rpc
import aioserial
import backoff
from serial.serialutil import SerialException
from serial.tools import list_ports
import structlog
import pyudev

from runtime import packet as packetlib
from runtime.frame import Frame, SensorUID
from runtime.service import Service
from runtime.service.storage import Document

from runtime.util import PacketTransportStatistics
from runtime.util.exception import RuntimeBaseException


def is_sensor(device: pyudev.Device) -> bool:
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


def get_com_ports(devices: typing.Iterable[pyudev.Device]) -> typing.Generator[str, None, None]:
    """ Translate udev devices into COM ports. """
    ports = list_ports.comports(include_links=True)
    for device in devices:
        for filename in pathlib.Path(device.sys_path).iterdir():
            if filename.name.startswith('tty'):
                for port in ports:
                    if port.location and port.location in device.sys_path:
                        yield port.device
                        break


class HotplugAction(enum.Enum):
    ADD = enum.auto()
    REMOVE = enum.auto()
    BIND = enum.auto()
    UNBIND = enum.auto()


class HotplugEvent(typing.NamedTuple):
    action: HotplugAction
    path: str
    ports: typing.List[str]


# Although all the fields added here are logically immutable, we cannot freeeze
# the class because the superclass needs to assign to some internal attributes.
# The unsafe hash is OK here.
@dataclasses.dataclass(unsafe_hash=True)
class SensorObserver(pyudev.MonitorObserver):
    """
    A background thread for monitoring low-level `udev` events asynchronously.

    The main thread containing the `asyncio` loop consumes `udev` events from a
    buffer that the observer enqueues to.
    """
    hotplug_events: asyncio.Queue = dataclasses.field(default_factory=asyncio.Queue)
    name: str = 'sensor-observer'
    subsystem: str = 'usb'
    device_type: str = 'usb_interface'
    context: pyudev.Context = dataclasses.field(default_factory=pyudev.Context)
    loop: asyncio.AbstractEventLoop = dataclasses.field(default_factory=asyncio.get_running_loop)

    def __post_init__(self):
        monitor = pyudev.Monitor.from_netlink(self.context)
        monitor.filter_by(self.subsystem, self.device_type)
        super().__init__(monitor, self.handle_event, name=self.name)

    def start(self):
        self.load_initial_sensors()
        super().start()

    def load_initial_sensors(self):
        """ Simulate `udev` ADD/BIND events for all sensors that are already plugged in. """
        for device in self.context.list_devices(subsystem=self.subsystem):
            self.handle_event(HotplugAction.ADD.name.lower(), device)
            self.handle_event(HotplugAction.BIND.name.lower(), device)

    def handle_event(self, action: str, device: pyudev.Device):
        if is_sensor(device):
            action = HotplugAction.__members__.get(action.upper())
            if action:
                event = HotplugEvent(action, device.device_path, [])
                if event.action is HotplugAction.ADD:
                    event.ports.extend(get_com_ports({device}))
                asyncio.run_coroutine_threadsafe(self.hotplug_events.put(event), self.loop)


@dataclasses.dataclass
class Sensor:
    """
    A Smart Sensor and an implementation of its initialize/read/write protocols.

    Attributes:
        connection: Serial connection.
        config: Connection to config store.
        logger: Logger.
        frame: Shared memory frame. Contains the device UID.
        ready: Flag that is set once the sensor type/UID is identified and the
            frame is allocated.
        heartbeats: Keys are heartbeat IDs of requests that are currently
            in-flight. The value is a flag that is set once the response has
            arrived.
    """
    connection: aioserial.AioSerial
    config: Document
    logger: structlog.BoundLoggerBase
    frame: typing.Optional[Frame] = None
    ready: asyncio.Event = dataclasses.field(default_factory=asyncio.Event)
    heartbeats: typing.Mapping[int, asyncio.Event] = \
        dataclasses.field(default_factory=lambda: collections.defaultdict(asyncio.Event))
    statistics: PacketTransportStatistics = \
        dataclasses.field(default_factory=PacketTransportStatistics)
    delimeter: typing.ClassVar[bytes] = b'\x00'

    @property
    def uid(self) -> typing.Optional[str]:
        return str(self.frame.control.uid) if self.frame else None

    async def _send(self, packet: packetlib.Packet):
        buffer = packet.encode()
        await self.connection.write_async(buffer)
        self.statistics.record_send(len(buffer))

    async def _recv(self) -> packetlib.Packet:
        buffer = await self.connection.read_until_async(self.delimeter)
        self.statistics.record_recv(len(buffer))
        return packetlib.Packet.decode(buffer)

    async def ping(self):
        await self._send(packetlib.make_ping())
        self.logger.debug('Pinged device')

    async def disable(self):
        await self._send(packetlib.make_disable())
        if self.frame:
            self.frame.reset()
        self.logger.debug('Disabled device')

    def get_random_heartbeat_id(self):
        choices = set(range(256)) - set(self.heartbeats.keys())
        return random.choice(tuple(choices))

    async def heartbeat(self, heartbeat_id: typing.Optional[int] = None,
                        timeout: typing.Optional[Real] = 2) -> int:
        if heartbeat_id is None:
            heartbeat_id = self.get_random_heartbeat_id()
        heartbeat_id = 0  # FIXME: It seems that Hibike identically sends the zero heartbeat ID.
        if heartbeat_id in self.heartbeats:
            raise RuntimeBaseException('Cannot use heartbeat ID of request in flight',
                                       heartbeat_id=heartbeat_id)
        complete, start = self.heartbeats[heartbeat_id], time.time()
        await self._send(packetlib.make_heartbeat_req(heartbeat_id))
        self.logger.debug('Heartbeat request sent', heartbeat_id=heartbeat_id)
        try:
            await asyncio.wait_for(complete.wait(), timeout)
        except asyncio.TimeoutError as exc:
            self.logger.error('Heartbeat request timed out', exc_info=exc)
            raise exc
        else:
            rtt = time.time() - start
            self.logger.debug('Heartbeat response received', heartbeat_id=heartbeat_id,
                              rtt=round(rtt, 5))
            return heartbeat_id
        finally:
            del self.heartbeats[heartbeat_id]

    async def discover(self, timeout: Real):
        """
        Discover the sensor type.

         1. Ping the sensor.
         2. The sensor responds with a subscription response with type/year.
         3. The read loop finds the sensor type in the catalog, allocates the
            frame in shared memory, and sets the ready flag.
         4. The device service advertises the existence of this sensor to other
            services over ZMQ.

        Raises::
            asyncio.TimeoutError: Device never responded with a subscription request.
        """
        await self.ping()
        # Block until the subscription request arrives.
        await asyncio.wait_for(self.ready.wait(), timeout)

    async def subscribe(self, params: typing.Collection[str], delay: Real = 0):
        delay_ms = int(1000*delay)
        if not 0 <= delay_ms <= 0xFFFF:
            raise RuntimeBaseException('Delay not in bounds', delay=delay)
        await self.ready.wait()
        bitmap = self.frame.to_bitmap(params)
        await self._send(packetlib.make_sub_req(bitmap, delay_ms))
        self.logger.debug('Sent subscription request', params=list(params), delay=delay)

    async def handle_subscription(self, packet: packetlib.Packet):
        uid = SensorUID.from_buffer_copy(packet.uid)
        if not self.ready.is_set():
            self.frame = Frame.open(uid.type_id, str(uid), create=True)
            self.frame.control.uid = uid
            self.logger = self.logger.bind(type=self.frame.__class__.__name__, uid=str(uid))
            self.logger.debug('Allocated frame')
            self.ready.set()

            params = {param.name for param in self.frame.params if param.subscribed}
            await self.subscribe(params, self.frame.delay)

        self.frame.control.subscription = packet.parameter_map
        self.frame.control.delay = packet.delay
        self.logger.debug('Received subscription response',
                          params=[param.name for param in self.frame.subscription],
                          year=uid.year,
                          delay=self.frame.control.delay/1000)

    async def handle_heartbeat(self, packet: packetlib.Packet):
        complete = self.heartbeats.get(packet.heartbeat_id)
        if not complete:
            self.logger.warn('Heartbeat response does not contain known ID',
                             heartbeat_id=packet.heartbeat_id)
        else:
            complete.set()

    async def handle_data(self, packet: packetlib.Packet):
        pass

    async def read_forever(self) -> typing.NoReturn:
        handlers = {
            packetlib.PacketType.HEARTBEAT_REQ: \
                (lambda packet: self._send(packetlib.make_heartbeat_res(packet.heartbeat_id))),
            packetlib.PacketType.HEARTBEAT_RES: self.handle_heartbeat,
            packetlib.PacketType.DEV_DATA: self.handle_data,
            packetlib.PacketType.SUB_RES: self.handle_subscription,
            packetlib.PacketType.ERROR: \
                (lambda packet: self.logger.error('Received error', err=packet.error_code)),
        }
        while True:
            try:
                packet = await self._recv()
            except packetlib.PacketEncodingException as exc:
                self.logger.warn('Packet encoding exception', exc=str(exc))
            else:
                await handlers[packet.type_id](packet)

    async def write_forever(self) -> typing.NoReturn:
        await self.ready.wait()
        assert self.frame
        while True:
            await asyncio.sleep(1)

    async def spin(self) -> typing.NoReturn:
        discovery_config = await self.config.get('device.discover')
        retry_strategy = backoff.on_exception(
            backoff.constant,
            asyncio.TimeoutError,
            max_tries=discovery_config['max_tries'],
            logger=self.logger,
        )

        try:
            done, pending = await asyncio.wait({
                retry_strategy(self.discover)(discovery_config['timeout']),
                self.read_forever(),
                self.write_forever(),
            }, return_when=asyncio.FIRST_EXCEPTION)
            for task in pending:
                task.cancel()
            for task in done:
                if task.exception():
                    self.logger.error('Sensor encountered exception', exc_info=task.exception())
        finally:
            self.connection.close()
            self.logger.debug('Serial connection closed')


@dataclasses.dataclass
class DeviceService(Service):
    sensors: typing.Mapping[str, Sensor] = dataclasses.field(default_factory=dict)

    def add_sensor(self, sensor: Sensor, wait: asyncio.Task):
        wait.exception()
        if sensor.uid in self.sensors:
            raise RuntimeBaseException('Sensor already exists')
        self.sensors[sensor.uid] = sensor

    def remove_sensor(self, sensor: Sensor, spin: asyncio.Task):
        spin.exception()
        if sensor.ready.is_set():
            self.sensors.pop(sensor.uid)

    async def dispatch_connections(self, hotplug_events: asyncio.Queue) -> typing.NoReturn:
        baud_rate = await self.config.get('device.baud_rate')
        while True:
            event = await hotplug_events.get()
            if event.action is HotplugAction.ADD:
                for port in event.ports:
                    connection = aioserial.AioSerial(port=port, baudrate=baud_rate)
                    self.logger.debug('Serial connection opened', port=port)
                    sensor = Sensor(connection, self.config, self.logger.bind(port=port))

                    ready = asyncio.create_task(sensor.ready.wait(), name='sensor-ready')
                    ready.add_done_callback(functools.partial(self.add_sensor, sensor))

                    spin = asyncio.create_task(sensor.spin(), name='sensor-spin')
                    spin.add_done_callback(functools.partial(self.remove_sensor, sensor))
            hotplug_events.task_done()

    async def broadcast_status(self, topic: str = ''):
        address = await self.config.get('device.addresses.status')
        interval = await self.config.get('device.status_interval')
        publisher = await aiozmq.rpc.connect_pubsub(bind=address)
        while True:
            await asyncio.sleep(interval)
            update = list(self.sensors.keys())
            await publisher.publish(topic).devices(update)

    async def main(self) -> typing.NoReturn:
        max_events = await self.config.get('device.max_hotplug_events')
        observer = SensorObserver(asyncio.Queue(max_events))
        observer.start()
        await asyncio.gather(
            super().main(),
            self.dispatch_connections(observer.hotplug_events),
            self.broadcast_status(),
        )

    def _get_sensors(self, *uids: str) -> typing.Iterable[Sensor]:
        if not uids:
            return self.sensors.keys()
        return [self.sensors[uid] for uid in uids]

    @aiozmq.rpc.method
    async def ping(self, *uids: str):
        """
        Ping the sensors with the given UIDs.

        Note::
            If any sensor does not exist, no sensor is pinged. If no UIDs are
            provided, all sensors will be pinged.
        """
        await asyncio.gather(*(sensor.ping() for sensor in self._get_sensors(*uids)))

    @aiozmq.rpc.method
    async def disable(self, *uids: str):
        """
        Disable sensors with the given UIDs.

        Note::
            Behavior is much the same as ``ping``.
        """
        await asyncio.gather(*(sensor.disable() for sensor in self._get_sensors(*uids)))

    @aiozmq.rpc.method
    async def subscribe(self, uid: str, params: typing.Collection[str], delay: Real = 0):
        """
        Subscribe to sensor parameters.

        Attributes:
            uid: Sensor unique identifier (integer format).
            params: List of parameter names.
            delay: Interval between data packet arrivals, in seconds.
        """
        await self.sensors[uid].subscribe(params, delay)

    @aiozmq.rpc.method
    async def heartbeat(self, uid: str, heartbeat_id: typing.Optional[int] = None,
                        timeout: typing.Optional[Real] = 2) -> int:
        """
        Send a heartbeat request and

        Attributes:
            uid: Sensor unique identifier (integer format).
            heartbeat_id: Heartbeat ID, randomly chosen if not provided.
            timeout: Duration in seconds to wait for the heartbeat response to arrive.
        """
        return await self.sensors[uid].heartbeat(heartbeat_id, timeout)

    async def get_health(self):
        await super().get_health()
        for uid, sensor in self.sensors.items():
            stats = sensor.statistics.as_dict()
            sensor.statistics.reset()
            start = time.time()
            await self.heartbeat(uid)
            stats['rtt'] = round(time.time() - start, 4)
            sensor.logger.info('Sensor health', **stats)

#     async def handle_dev_data(self, packet):
#         offset, param_buf = 0, memoryview(bytearray(packet.payload[2:]))
#         await self.ready.wait()
#         for param in self.buffer.struct.get_parameters(packet.parameter_map):
#             size = ctypes.sizeof(param.type)
#             value = param.type.from_buffer(param_buf[offset: offset + size])
#             self.buffer.struct.set_current(param.name, value)
#             offset += size
#         if offset != len(param_buf):
#             raise RuntimeBaseException('DEV_DATA payload contains extra data')
#
#     async def write_loop(self, cycle_period: int = 1000):
#         await self.ready.wait()
#         loop = asyncio.get_running_loop()
#         start, count = loop.time(), 0
#         while True:
#             await asyncio.sleep(self.write_interval)
#             if not self.buffer.struct:
#                 break
#
#             packet = self.buffer.struct.make_write()
#             if packet:
#                 await packetlib.send(self.serial_conn, packet)
#             packet = self.buffer.struct.make_read()
#             if packet:
#                 await packetlib.send(self.serial_conn, packet)
#
#             count = (count + 1) % cycle_period
#             if count == 0:
#                 end = loop.time()
#                 start, frequency = end, round(cycle_period / (end - start), 3)
#                 LOGGER.debug('Estimated parameter write frequency',
#                              frequency=frequency, uid=self.buffer.struct.uid.to_int())
