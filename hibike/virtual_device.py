"""
This program creates a virtual hibike device for testing purposes.

usage:
$ socat -d -d pty,raw,echo=0 pty,raw,echo=0
2016/09/20 21:29:03 socat[4165] N PTY is /dev/pts/26
2016/09/20 21:29:03 socat[4165] N PTY is /dev/pts/27
2016/09/20 21:29:03 socat[4165] N starting data transfer loop with FDs [3,3] and [5,5]
$ python3.5 virtual_device.py -d LimitSwitch -p /dev/pts/26
"""
import argparse
import asyncio
import json
import random
import struct
import time

# pylint: disable=import-error
import serial_asyncio
import hibike_message as hm


# Format of default values storage:
# {"DeviceName": {"param1": value1, "param2": value2}}
DEFAULT_VALUES_FILE = "virtual_device_defaults.json"
with open(DEFAULT_VALUES_FILE) as f:
    DEFAULT_VALUES = json.load(f)


class VirtualDevice(asyncio.Protocol):
    """
    A fake Hibike smart sensor.
    """
    HEARTBEAT_DELAY_MS = 100
    PACKET_BOUNDARY = bytes([0])
    def __init__(self, uid, event_loop, verbose=False):
        self.uid = uid
        self.event_loop = event_loop
        self._ready = asyncio.Event(loop=event_loop)
        self.serial_buf = bytearray()
        self.read_queue = asyncio.Queue(loop=event_loop)
        self.verbose = verbose

        self.update_time = 0
        self.delay = 0
        self.transport = None

        self.response_map = {
            hm.MESSAGE_TYPES["Ping"]: self._process_ping,
            hm.MESSAGE_TYPES["SubscriptionRequest"]: self._process_sub_request,
            hm.MESSAGE_TYPES["DeviceRead"]: self._process_device_read,
            hm.MESSAGE_TYPES["DeviceWrite"]: self._process_device_write,
            hm.MESSAGE_TYPES["Disable"]: self._process_disable,
            hm.MESSAGE_TYPES["HeartBeatResponse"]: self._process_heartbeat_response,
        }
        self.param_values = DEFAULT_VALUES[hm.uid_to_device_name(uid)]
        self.subscribed_params = set()

        event_loop.create_task(self.process_messages())
        event_loop.create_task(self.send_subscribed_params())
        event_loop.create_task(self.request_heartbeats())

    def data_received(self, data):
        self.serial_buf.extend(data)
        zero_loc = self.serial_buf.find(bytes([0]))
        if zero_loc != -1:
            self.serial_buf = self.serial_buf[zero_loc:]
            packet = hm.parse_bytes(self.serial_buf)
            if packet != None:
                self.serial_buf = self.serial_buf[1:]
                self.read_queue.put_nowait(packet)
            elif self.serial_buf.count(self.PACKET_BOUNDARY) > 1:
                new_packet = self.serial_buf[1:].find(self.PACKET_BOUNDARY) + 1
                self.serial_buf = self.serial_buf[new_packet:]


    def verbose_log(self, fmt_string, *fmt_args):
        """Log a message if verbosity is enabled."""
        if self.verbose:
            print(fmt_string.format(*fmt_args))

    async def process_messages(self):
        """Process recieved messages."""
        await self._ready.wait()
        while not self.transport.is_closing():
            msg = await self.read_queue.get()
            msg_type = msg.get_message_id()
            if msg_type not in self.response_map:
                continue
            self.response_map[msg_type](msg)

    async def send_subscribed_params(self):
        """Send values of subscribed parameters at a regular interval."""
        await self._ready.wait()
        device_id = hm.uid_to_device_id(self.uid)
        while not self.transport.is_closing():
            await asyncio.sleep(0.005, loop=self.event_loop)
            if self.update_time != 0 and self.delay != 0:
                if time.time() - self.update_time >= self.delay * 0.001:
                    # If the time equal to the delay has elapsed since the previous device data,
                    # send a device data with the device id
                    # and the device's subscribed params and values
                    data = []
                    for param in self.subscribed_params:
                        data.append((param, self.param_values[param]))
                    hm.send(self.transport, hm.make_device_data(device_id, data))
                    self.update_time = time.time()
                    self.verbose_log("Regular data update sent from {}",
                                     hm.uid_to_device_name(self.uid))

    async def request_heartbeats(self):
        """Request heartbeats on a regular basis."""
        await self._ready.wait()
        while not self.transport.is_closing():
            await asyncio.sleep(self.HEARTBEAT_DELAY_MS/1000, loop=self.event_loop)
            hm.send(self.transport, hm.make_heartbeat_request())

    # pylint: disable=unused-argument
    def _process_ping(self, msg):
        """Respond to a ping packet."""
        self.verbose_log("Ping received")
        dev_id = hm.uid_to_device_id(self.uid)
        hm.send(self.transport, hm.make_subscription_response(dev_id, [], 0, self.uid))

    def _process_sub_request(self, msg):
        """Respond to a subscription request with an appropriate response."""
        self.update_time = time.time()
        dev_id = hm.uid_to_device_id(self.uid)
        self.verbose_log("Subscription request received")
        params, delay = struct.unpack("<HH", msg.get_payload())
        subscribed_params = hm.decode_params(dev_id, params)
        hm.send(self.transport,
                hm.make_subscription_response(dev_id, subscribed_params, delay, self.uid))
        self.delay = delay
        self.subscribed_params.update(set(subscribed_params))

    def _process_device_read(self, msg):
        self.verbose_log("Device read received")
        device_id = hm.uid_to_device_id(self.uid)
        # Send a device data with the requested param and value tuples
        params, = struct.unpack("<H", msg.get_payload())
        read_params = hm.decode_params(device_id, params)
        read_data = []

        for param in read_params:
            if not (hm.readable(device_id, param) and param in self.param_values):
                raise ValueError("Tried to read unreadable parameter {}".format(param))
            read_data.append((param, self.param_values[param]))
        hm.send(self.transport, hm.make_device_data(device_id, read_data))

    def _process_device_write(self, msg):
        # Write to requested parameters
        # and return the values of the parameters written to using a device data
        self.verbose_log("Device write received")
        device_id = hm.uid_to_device_id(self.uid)
        write_params_and_values = hm.decode_device_write(msg, device_id)

        for (param, value) in write_params_and_values:
            if not (hm.writable(device_id, param) and param in self.param_values):
                raise ValueError("Tried to write read-only parameter: {}".format(param))
            self.param_values[param] = value

        updated_params = []
        for (param, value) in write_params_and_values:
            if hm.readable(device_id, param):
                updated_params.append((param, value))
        hm.send(self.transport, hm.make_device_data(device_id, updated_params))

    def _process_disable(self, msg):
        pass

    def _process_heartbeat_response(self, msg):
        pass

    def connection_made(self, transport):
        self.transport = transport
        self._ready.set()

    def connection_lost(self, exc):
        """
        If this happens, we're shutting down anyways,
        so don't do anything.
        """
        pass


def main():
    """
    Create virtual devices and send test data on them.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', required=True, help='device type')
    parser.add_argument('-p', '--port', required=True, help='serial port')
    parser.add_argument('-v', '--verbose',
                        help='print messages when sending and receiving packets',
                        action="store_true")
    args = parser.parse_args()

    def verbose_log(fmt_string, *fmt_args):
        """
        Log a message using a formatting string if verbosity
        is enabled.
        """
        if args.verbose:
            print(fmt_string.format(*fmt_args))

    device = args.device
    port = args.port
    verbose_log("Device {} on port {}", device, port)

    for device_num in hm.DEVICES:
        if hm.DEVICES[device_num]["name"] == device:
            device_id = device_num
            break
    else:
        raise RuntimeError("Invalid Device Name!!!")


    year = 1
    randomness = random.getrandbits(64)
    uid = (device_id << 72) | (year << 64) | randomness
    event_loop = asyncio.get_event_loop()

    def protocol_factory():
        """Create a VirtualDevice with filled-in parameters."""
        return VirtualDevice(uid, event_loop, args.verbose)

    event_loop.create_task(serial_asyncio.create_serial_connection(event_loop, protocol_factory,
                                                                   port, baudrate=115200))
    event_loop.run_forever()


if __name__ == "__main__":
    main()
