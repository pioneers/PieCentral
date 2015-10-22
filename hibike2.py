import os
import sys
import serial
import binascii
import time

sys.path.append(os.getcwd())

from hibike_message2 import *

# uids - {port: uid}
# devices - {port : devicetype}
# data - {port : data}

class Hibike():
    def __init__(self):
        self._uids = dict()
        self._devices = dict()
        self._data = dict()
        self._connections = dict()

        self._enumerateSerialPorts()


    def getEnumeratedDevices(self):
        return dict(self._devices)

    # TODO
    def subToDevices(self, devices):
        for device in devices:
            pass


    # returns the latest device reading, given its port
    def getData(self, port):
        return self._data[port]

    def writeData(self, port):
        raise NotImplementedError

    def _getPorts(self):
        return ['/dev/%s' % port for port in os.listdir("/dev/") 
                if port[:6] == "ttyUSB"]

    def _enumerateSerialPorts(self):
        ports = self._getPorts()
        serial_conns = {p: Serial.serial(p, 115200) for p in ports}
        pingMsg = HibikeMessage(messageTypes['SubscriptionRequest'], 
                                bytearray([0]))

        for p in ports: send(pingMsg, serial_conns[p])
        time.sleep(0.1)
        for p in ports:
            msg = read(serial_conns[p])
            if msg == None or msg == -1:
                print("ping response failed.")
                continue

            uid = int(binascii.hexlify(msg.getPayload(), 16))
            self._uids[p] = uid
            self._devices[p] = getDeviceType(uid)
            self._data[p] = 0
            self._connections[p] = serial_conns[p]


    def _spawnHibikeThread(self):
        pass


# TODO: implement multithreading :)
class HibikeThread():
    def __init__(self):
        pass

    def checkSerialPorts(self):
        pass