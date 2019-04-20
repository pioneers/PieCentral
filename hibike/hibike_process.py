"""
The main Hibike process.
"""
import asyncio
import glob
import os
import sys
import random
import time

import serial_asyncio
import aioprocessing
import aiofiles


import hibike_message as hm
try:
    import hibike_packet
    USING_PACKET_EXTENSION = True
except ImportError:
    USING_PACKET_EXTENSION = False

__all__ = ["hibike_process"]

# .04 milliseconds sleep is the same frequency we subscribe to devices at
BATCH_SLEEP_TIME = .04
# Time in seconds to wait until reading from a potential sensor
IDENTIFY_TIMEOUT = 1
# Time in seconds to wait between checking for new devices
# and cleaning up old ones.
HOTPLUG_POLL_INTERVAL = 1
# Whether to use profiling or not. On the BBB, profiling adds a significant overhead (~30%).
USE_PROFILING = False
# Where to output profiling statistics. By default, this is in Callgrind format
PROFILING_OUTPUT_FILE = "func_stats"
# The time period to take measurements over, in seconds
PROFILING_PERIOD = 60
PAUSE_QUEUE_SIZE = 10
RESUME_QUEUE_SIZE = 2

def scan_for_serial_ports():
    """
    Scan for serial ports that look like an Arduino.
    """
    # Last command is included so that it's compatible with OS X Sierra
    # Note: If you are running OS X Sierra, do not access the directory through vagrant ssh
    # Instead access it through Volumes/vagrant/PieCentral
    return set(glob.glob("/dev/ttyACM*") +\
               glob.glob("/dev/ttyUSB*") +\
               glob.glob("/dev/tty.usbmodem*"))


async def get_working_serial_ports(event_loop, excludes=()):
    """
    Scan for open COM ports, except those in `excludes`.

    Returns:
        A list of port names.
    """
    excludes = set(excludes)
    ports = await event_loop.run_in_executor(None, scan_for_serial_ports)
    try:
        virtual_device_config_file = os.path.join(os.path.dirname(__file__), "virtual_devices.txt")
        async with aiofiles.open(virtual_device_config_file, loop=event_loop) as f:
            contents = await f.read()
            ports.update(contents.split())
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
        port_names = set([dev.transport.serial.name for dev in devices.values()\
                          if dev.transport is not None and dev.transport.serial is not None])
        port_names.update(pending)
        new_serials = await get_working_serial_ports(event_loop, port_names)
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

    :param dict devices: Mapping from UIDs to devices
    :param dict batched_data: Mapping from UIDs to device state
    :param asyncio.Queue error_queue: Info about disconnects goes here
    :param aioprocessing.Queue state_queue: Connection to StateManager
    :param event_loop: The event loop
    :param set pending: Set of serial connections that may or may not
    have devices on them.
    """
    PACKET_BOUNDARY = bytes([0])
    __slots__ = ("uid", "write_queue", "batched_data", "read_queue", "error_queue",
                 "state_queue", "instance_id", "transport", "_ready", "serial_buf")
    # pylint: disable=too-many-arguments
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
        if USING_PACKET_EXTENSION:
            # pylint: disable=no-member
            self.serial_buf = hibike_packet.RingBuffer()
        else:
            self.serial_buf = bytearray()

        event_loop.create_task(self.register_sensor(event_loop, devices, pending))
        event_loop.create_task(self.send_messages())
        event_loop.create_task(self.recv_messages())

    async def register_sensor(self, event_loop, devices, pending):
        """
        Try to get our UID from the sensor and register it with `hibike_process`.
        """
        await self._ready.wait()
        hm.send(self.transport, hm.make_ping())
        await asyncio.sleep(IDENTIFY_TIMEOUT, loop=event_loop)
        if self.uid is None:
            self.quit()
        else:
            hm.send(self.transport, hm.make_ping())
            hm.send(self.transport,
                    hm.make_subscription_request(hm.uid_to_device_id(self.uid), [], 0))
            devices[self.uid] = self
        pending.remove(self.transport.serial.name)

    async def send_messages(self):
        """
        Send messages in the queue to the sensor.
        """
        await self._ready.wait()
        while not self.transport.is_closing():
            instruction, args = await self.write_queue.get()
            if instruction == "ping":
                hm.send(self.transport, hm.make_ping())
            elif instruction == "subscribe":
                uid, delay, params = args
                hm.send(self.transport,
                        hm.make_subscription_request(hm.uid_to_device_id(uid),
                                                     params, delay))
            elif instruction == "read":
                uid, params = args
                hm.send(self.transport, hm.make_device_read(hm.uid_to_device_id(uid), params))
            elif instruction == "write":
                uid, params_and_values = args
                hm.send(self.transport, hm.make_device_write(hm.uid_to_device_id(uid),
                                                             params_and_values))
            elif instruction == "disable":
                hm.send(self.transport, hm.make_disable())
            elif instruction == "heartResp":
                uid = args[0]
                hm.send(self.transport, hm.make_heartbeat_response(self.read_queue.qsize()))

    async def recv_messages(self):
        """
        Process received messages.
        """
        await self._ready.wait()
        while not self.transport.is_closing():
            if self.read_queue.qsize() >= PAUSE_QUEUE_SIZE:
                self.transport.pause_reading()
            if self.read_queue.qsize() <= RESUME_QUEUE_SIZE:
                self.transport.resume_reading()
            packet = await self.read_queue.get()
            message_type = packet.get_message_id()
            if message_type == hm.MESSAGE_TYPES["SubscriptionResponse"]:
                params, delay, uid = hm.parse_subscription_response(packet)
                self.uid = uid
                await self.state_queue.coro_put(("device_subscribed", [uid, delay, params]))
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

    if USING_PACKET_EXTENSION:
        def data_received(self, data):
            self.serial_buf.extend(data)
            # pylint: disable=no-member
            maybe_packet = hibike_packet.process_buffer(self.serial_buf)
            if maybe_packet is not None:
                message_id, payload = maybe_packet
                message = hm.HibikeMessage(message_id, payload)
                self.read_queue.put_nowait(message)
    else:
        def data_received(self, data):
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
            error = Disconnect(uid=self.uid, instance_id=self.instance_id, accessed=False)
            self.error_queue.put_nowait(error)


class Disconnect:
    """
    Information about a device disconnect.
    """
    def __init__(self, uid, instance_id, accessed):
        self.uid = uid
        self.instance_id = instance_id
        self.accessed = accessed


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


async def print_profiler_stats(event_loop, time_delay):
    """
    Print profiler statistics after a number of seconds.
    """
    try:
        import yappi
    except ImportError:
        return
    await asyncio.sleep(time_delay, loop=event_loop)
    print("Printing profiler stats")
    yappi.get_func_stats().print_all(out=sys.stdout,
                                     columns={0: ("name", 60), 1: ("ncall", 5), 2: ("tsub", 8),
                                              3: ("ttot", 8), 4: ("tavg", 8)})
    yappi.get_func_stats().save(PROFILING_OUTPUT_FILE, type="callgrind")
    yappi.get_thread_stats().print_all()


class QueueContext:
    """
    Stub to force aioprocessing to use an existing queue.
    """
    def __init__(self, queue):
        self._queue = queue

    # pylint: disable=invalid-name
    def Queue(self, _size):
        return self._queue


def hibike_process(bad_things_queue, state_queue, pipe_from_child):
    """
    Run the main hibike processs.
    """
    pipe_from_child = aioprocessing.AioConnection(pipe_from_child)
    # By default, AioQueue instantiates a new Queue object, but we
    # don't want that.
    state_queue = aioprocessing.AioQueue(context=QueueContext(state_queue))
    bad_things_queue = aioprocessing.AioQueue(context=QueueContext(bad_things_queue))

    devices = {}
    batched_data = {}
    event_loop = asyncio.get_event_loop()
    error_queue = asyncio.Queue(loop=event_loop)

    event_loop.create_task(batch_data(batched_data, state_queue, event_loop))
    event_loop.create_task(hotplug_async(devices, batched_data, error_queue,
                                         state_queue, event_loop))
    event_loop.create_task(dispatch_instructions(devices, bad_things_queue, state_queue,
                                                 pipe_from_child, event_loop))
    # start event loop
    if USE_PROFILING:
        try:
            import yappi
            yappi.start()
            event_loop.create_task(print_profiler_stats(event_loop, PROFILING_PERIOD))
        except ImportError:
            print("Unable to import profiler. Make sure you installed with the '--dev' flag.")

    event_loop.run_forever()


async def dispatch_instructions(devices, bad_things_queue, state_queue,
                                pipe_from_child, event_loop):
    """
    Respond to instructions from `StateManager`.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    parent_path = path.rstrip("hibike")
    runtime = os.path.join(parent_path, "runtime")
    sys.path.insert(1, runtime)
    # Pylint doesn't understand our import shenanigans
    # pylint: disable=import-error
    import runtimeUtil

    while True:
        instruction, args = await pipe_from_child.coro_recv(loop=event_loop)
        try:
            if instruction == "enumerate_all":
                for pack in devices.values():
                    pack.write_queue.put_nowait(("ping", []))
            elif instruction == "subscribe_device":
                uid = args[0]
                devices[uid].write_queue.put_nowait(("subscribe", args))
            elif instruction == "write_params":
                uid = args[0]
                devices[uid].write_queue.put_nowait(("write", args))
            elif instruction == "read_params":
                uid = args[0]
                devices[uid].write_queue.put_nowait(("read", args))
            elif instruction == "disable_all":
                for pack in devices.values():
                    pack.write_queue.put_nowait(("disable", []))
            elif instruction == "timestamp_down":
                timestamp = time.time()
                args.append(timestamp)
                await state_queue.coro_put(("timestamp_up", args), loop=event_loop)
        except KeyError as e:
            await bad_things_queue.coro_put(runtimeUtil.BadThing(
                sys.exc_info(),
                str(e),
                event=runtimeUtil.BAD_EVENTS.HIBIKE_NONEXISTENT_DEVICE))
        except TypeError as e:
            await bad_things_queue.coro_put(runtimeUtil.BadThing(
                sys.exc_info(),
                str(e),
                event=runtimeUtil.BAD_EVENTS.HIBIKE_INSTRUCTION_ERROR))
