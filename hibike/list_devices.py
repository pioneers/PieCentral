"""
List serial ports and read data from listed ports.

Does not actually work at the moment.
"""
# pylint: skip-file
# TODO: Fix or delete this file
import glob
import struct
import time
from collections import defaultdict

import serial
import hibike_message as hm

PORTS = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
print("ports:", PORTS)


class HibikeDevice:

    def __init__(self, serial_port, params, delay, uid):
        self.serial_port = serial_port
        self.uid = uid
        self.device_type = hm.uid_to_device_id(uid)
        self.params = params
        self.delay = delay
        self.data = defaultdict(lambda: (None, -1))

    def subscription_response(self, params, delay, uid):
        self.uid = uid
        self.params = params
        self.delay = delay

    def device_data(self, data):
        self.data.update({param: (value, time.time())})

    def __str__(self):
        res = ""
        res += hm.uid_to_device_name(self.uid)
        res += ":\n"
        res += "    %d\n" % self.uid
        res += "    %s\n" % self.serial_port.port
        res += "    %s\n" % self.data
        return res
    def __repr__(self):
        res = ""
        res += hm.uid_to_device_name(self.uid)
        res += ":\n"
        res += "    %d" % self.uid
        res += "    %s\n" % self.serial_port.port
        res += "    %s\n" % self.data
        return res

SERIALS = [serial.Serial(port, 115200) for port in PORTS]
DEVICES = [] 

for s in SERIALS:
    hm.send(s, hm.make_ping())

while SERIALS:
    remaining = []
    for s in SERIALS:
        reading = hm.blocking_read(s)
        if reading:
            params, delay, device_type, year, id = struct.unpack("<HHHBQ", reading.get_payload())
            uid = (device_type << 72) | (year << 64) | id
            DEVICES.append(HibikeDevice(s, params, delay, uid))
        else:
            remaining.append(s)
    SERIALS = remaining

print("devices:", DEVICES)

for device in DEVICES:
    hm.send(device.serial_port,
            hm.make_subscription_request(device.device_type,
                                         hm.all_params_for_device_id(device.device_type), 10))

while True:
    for device in DEVICES:
        reading = hm.blocking_read(device.serial_port)
        if reading:
            if reading.get_message_id() == hm.MESSAGE_TYPES["DeviceData"]:
                print(reading.get_payload())
