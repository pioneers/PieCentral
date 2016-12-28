import glob
import serial
import hibike_message as hm
import struct
import time
from collections import defaultdict
ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
print("ports:", ports)


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

serials = [serial.Serial(port, 115200) for port in ports]
devices = []


for s in serials:
    hm.send(s, hm.make_ping())

while serials:
    remaining = []
    for s in serials:
        reading = hm.blocking_read(s)
        if reading:
            params, delay, device_type, year, id = struct.unpack("<HHHBQ", reading.getPayload())
            uid = (device_type << 72) | (year << 64) | id
            devices.append(HibikeDevice(s, params, delay, uid))
        else:
            remaining.append(s)
    serials = remaining

print("devices:", devices)

for device in devices:
    hm.send(device.serial_port, hm.make_subscription_request(device.device_type, hm.all_params_for_device_id(device.device_type), 10))

while True:
    for device in devices:
        reading = hm.blocking_read(device.serial_port)
        if reading:
            if reading.getmessageID() == hm.messageTypes["DeviceData"]:
                print(reading.getPayload())
