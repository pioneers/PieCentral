"""
The main Hibike process.
"""
import asyncio
from collections import namedtuple
import glob
import os
import queue
import random
import time

# pylint: disable=import-error
import hibike_message as hm
import serial_asyncio
import aioprocessing
__all__ = ["hibike_process"]


# .04 milliseconds sleep is the same frequency we subscribe to devices at
BATCH_SLEEP_TIME = .04
# Time in seconds to wait until reading from a potential sensor
IDENTIFY_TIMEOUT = 1
# Time in seconds to wait between checking for new devices
# and cleaning up old ones.
HOTPLUG_POLL_INTERVAL = 1


def get_working_serial_ports(excludes=()):
    """
    Scan for open COM ports, except those in `excludes`.

    Returns:
        A list of port names.
    """
    excludes = set(excludes)
    # Last command is included so that it's compatible with OS X Sierra
    # Note: If you are running OS X Sierra, do not access the directory through vagrant ssh
    # Instead access it through Volumes/vagrant/PieCentral
    ports = set(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
                + glob.glob("/dev/tty.usbmodem*"))
    try:
        virtual_device_config_file = os.path.join(os.path.dirname(__file__), "virtual_devices.txt")
        ports.update(open(virtual_device_config_file, "r").read().split())
    except IOError:
        pass
    ports.difference_update(excludes)
    return list(ports)

  
async def hotplug_async(devices, batched_data, error_queue, state_queue, event_loop):
    """
    Scan for new devices on serial ports and automatically spin them up.
    """
    pending = set()
    def protocol_factory():
        """
        Create a `SmartSensorProtocol` with necessary parameters filled in.
        """
        return SmartSensorProtocol(devices, batched_data, error_queue,
                                   state_queue, event_loop, pending)

    while True:
        await asyncio.sleep(HOTPLUG_POLL_INTERVAL, loop=event_loop)
        port_names = set(map(lambda dev: dev.transport.serial.name, devices.values()))
        port_names.update(pending)
        new_serials = get_working_serial_ports(port_names)
        for port in new_serials:
            try:
                pending.add(port)
                await serial_asyncio.create_serial_connection(event_loop, protocol_factory, port,
                                                              baudrate=115200)
            except serial_asyncio.serial.SerialException:
                pass
        await remove_disconnected_devices(error_queue, devices, state_queue, event_loop)


class SmartSensorProtocol(asyncio.Protocol):
    """
    Handle communication over serial with a smart sensor.
    """
    PACKET_BOUNDARY = bytes([0])
    def __init__(self, devices, batched_data, error_queue, state_queue, event_loop, pending: set):
        # We haven't found out what our UID is yet
        self.uid = None

        self.write_queue = asyncio.Queue(loop=event_loop)
        self.batched_data = batched_data
        self.read_queue = asyncio.Queue(loop=event_loop)
        self.error_queue = error_queue
        self.state_queue = state_queue
        self.instance_id = random.getrandbits(128)

        self.transport = None
        self._ready = asyncio.Event(loop=event_loop)
        self.serial_buf = bytearray()

        async def register_sensor():
            """
            Register this sensor with `hibike_process`, if possible.
            """
            await self._ready.wait()
            hm.send_transport(self.transport, hm.make_ping())
            await asyncio.sleep(IDENTIFY_TIMEOUT, loop=event_loop)
            if self.uid is None:
                self.quit()
            else:
                hm.send_transport(self.transport, hm.make_ping())
                hm.send_transport(self.transport,
                                  hm.make_subscription_request(hm.uid_to_device_id(self.uid),
                                                               [], 0))
                devices[self.uid] = self
            pending.remove(self.transport.serial.name)

        event_loop.create_task(self.send_messages())
        event_loop.create_task(self.recv_messages())
        event_loop.create_task(register_sensor())

    async def send_messages(self):
        """
        Send messages in the queue to the sensor.
        """
        await self._ready.wait()
        while not self.transport.is_closing():
            instruction, args = await self.write_queue.get()
            if instruction == "ping":
                hm.send_transport(self.transport, hm.make_ping())
            elif instruction == "subscribe":
                uid, delay, params = args
                hm.send_transport(self.transport,
                                  hm.make_subscription_request(hm.uid_to_device_id(uid),
                                                               params, delay))
            elif instruction == "read":
                uid, params = args
                hm.send_transport(self.transport, hm.make_device_read(hm.uid_to_device_id(uid),
                                                                      params))
            elif instruction == "write":
                uid, params_and_values = args
                hm.send_transport(self.transport, hm.make_device_write(hm.uid_to_device_id(uid),
                                                                       params_and_values))
            elif instruction == "disable":
                hm.send_transport(self.transport, hm.make_disable())
            elif instruction == "heartResp":
                uid = args[0]
                hm.send_transport(self.transport, hm.make_heartbeat_response())

    async def recv_messages(self):
        """
        Process received messages.
        """
        await self._ready.wait()
        while not self.transport.is_closing():
            packet = await self.read_queue.get()
            message_type = packet.get_message_id()
            if message_type == hm.MESSAGE_TYPES["SubscriptionResponse"]:
                params, delay, uid = hm.parse_subscription_response(packet)
                self.uid = uid
                self.state_queue.put_nowait(("device_subscribed", [uid, delay, params]))
            elif message_type == hm.MESSAGE_TYPES["DeviceData"]:
                # This is kind of a hack, but it allows us to use `recv_messages` for
                # detecting new smart sensors as well as reading from known ones.
                if self.uid is not None:
                    params_and_values = hm.parse_device_data(packet, hm.uid_to_device_id(self.uid))
                    self.batched_data[uid] = params_and_values
            elif message_type == hm.MESSAGE_TYPES["HeartBeatRequest"]:
                if self.uid is not None:
                    self.write_queue.put_nowait(("heartResp", [self.uid]))

    def connection_made(self, transport):
        self.transport = transport
        self._ready.set()

    def quit(self):
        """
        Stop processing packets and close the serial connection.
        """
        self.transport.abort()

    def data_received(self, data):
        """
        Attempt to parse data from the serial port into
        a Hibike packet.
        """
        self.serial_buf.extend(data)
        zero_loc = self.serial_buf.find(self.PACKET_BOUNDARY)
        if zero_loc != -1:
            self.serial_buf = self.serial_buf[zero_loc:]
            packet = hm.parse_bytes(self.serial_buf)
            if packet != None:
                # Chop off a byte so we don't output this packet again
                self.serial_buf = self.serial_buf[1:]
                self.read_queue.put_nowait(packet)
            elif self.serial_buf.count(self.PACKET_BOUNDARY) > 1:
                # If there's another packet in the buffer
                # we can safely jump to it for the next iteration
                new_packet = self.serial_buf[1:].find(self.PACKET_BOUNDARY) + 1
                self.serial_buf = self.serial_buf[new_packet:]

    def connection_lost(self, exc):
        if self.uid is not None:
            error = namedtuple("Disconnect", ["uid", "instance_id", "accessed"])
            error.uid = self.uid
            error.instance_id = self.instance_id
            error.accessed = False
            self.error_queue.put_nowait(error)


async def remove_disconnected_devices(error_queue, devices, state_queue, event_loop):
    """
    Clean up any disconnected devices in `error_queue`.
    """
    next_time_errors = []
    while True:
        try:
            error = error_queue.get_nowait()
            pack = devices[error.uid]
            if not error.accessed:
                # Wait until the next cycle to make sure it's disconnected
                error.accessed = True
                next_time_errors.append(error)
                continue
            elif error.instance_id != pack.instance_id:
                # The device has reconnected in the meantime
                continue
            uid = error.uid
            del devices[uid]
            await state_queue.coro_put(("device_disconnected", [uid]), loop=event_loop)
        except asyncio.QueueEmpty:
            for err in next_time_errors:
                error_queue.put_nowait(err)
            return


async def batch_data(sensor_values, state_queue, event_loop):
    """
    Periodically send sensor values to `StateManager`.
    """
    while True:
        await asyncio.sleep(BATCH_SLEEP_TIME, loop=event_loop)
        await state_queue.coro_put(("device_values", [sensor_values]), loop=event_loop)


# pylint: disable=unused-argument
def hibike_process(bad_things_queue, state_queue, pipe_from_child):
    """
    Run the main hibike processs.
    """
    # By default, AioQueue instantiates a new Queue object, but we
    # don't want that.
    old_queue_context = namedtuple("StateManagerQueue", ["Queue"])
    old_queue_context.Queue = lambda size: state_queue
    pipe_from_child = aioprocessing.AioConnection(pipe_from_child)
    state_queue = aioprocessing.AioQueue(context=old_queue_context)

    devices = {}
    batched_data = {}
    event_loop = asyncio.get_event_loop()
    error_queue = asyncio.Queue(loop=event_loop)

    event_loop.create_task(batch_data(batched_data, state_queue, event_loop))
    event_loop.create_task(hotplug_async(devices, batched_data, error_queue,
                                         state_queue, event_loop))
    event_loop.create_task(dispatch_instructions(devices, state_queue, pipe_from_child, event_loop))
    # start event loop
    event_loop.run_forever()


async def dispatch_instructions(devices, state_queue, pipe_from_child, event_loop):
    """
    Respond to instructions from `StateManager`.
    """
    while True:
        instruction, args = await pipe_from_child.coro_recv(loop=event_loop)
        try:
            if instruction == "enumerate_all":
                for pack in devices.values():
                    pack.write_queue.put_nowait(("ping", []))
            elif instruction == "subscribe_device":
                uid = args[0]
                if uid in devices:
                    devices[uid].write_queue.put_nowait(("subscribe", args))
            elif instruction == "write_params":
                uid = args[0]
                if uid in devices:
                    devices[uid].write_queue.put_nowait(("write", args))
            elif instruction == "read_params":
                uid = args[0]
                if uid in devices:
                    devices[uid].write_queue.put_nowait(("read", args))
            elif instruction == "disable_all":
                for pack in devices.values():
                    pack.write_queue.put_nowait(("disable", []))
            elif instruction == "timestamp_down":
                timestamp = time.time()
                args.append(timestamp)
                await state_queue.coro_put(("timestamp_up", args), loop=event_loop)
        except KeyError:
            print("Tried to access a nonexistent device")