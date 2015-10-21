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

        self.enumerateSerialPorts()
        for device in self._devices:
            # TODO: send sub requests
            pass

    def getEnumeratedDevices():
        return dict(self._devices)

    # returns the latest device reading, given its port
    def getDeviceReading(self, port):
        return self._data[port]

    def _getPorts(self):
        # TODO: find and return all active USB ports
        return ['/dev/ttyUSB0']

    def _enumerateSerialPorts(self):
        ports = self._getPorts()
        serialList = [Serial.serial(p, 115200) for p in ports]
        pingMsg = HibikeMessage(messageTypes['SubscriptionRequest'], 
                                bytearray([0]))

        for p in ports: send(pingMsg)
        time.sleep(0.1)
        for p in ports:
            msg = read(p)
            if msg == None or msg == -1:
                print("ping response failed.")

            uid = int(binascii.hexlify(msg.getPayload(), 16))
            self._uids[p] = uid
            self._devices[p] = getDeviceType(uid)
            self._data[p] = 0

    def _spawnHibikeThread(self):
        pass


# TODO: implement multithreading :)
class HibikeThread():
    def __init__(self):
        pass

    def checkSerialPorts(self):
        pass