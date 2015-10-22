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
# connections - {port : Serial}
# ports - {uid: port}

class Hibike():
    def __init__(self):
        self._uids = dict()
        self._devices = dict()
        self._data = dict()
        self._connections = dict()
        self._ports = dict()

        self._enumerateSerialPorts()


    def getEnumeratedDevices(self):
        return dict(self._devices)

    # TODO decide on how to handle failures
    # devices = [(UID, delay)]
    def subToDevices(self, devices):
        errors = []
        for UID, delay in devices:
            subReq = HibikeMessage(messageTypes['SubscriptionRequest'], 
                                bytearray([delay]))
            serial_conn = self._connections[self._ports[UID]]
            send(subReq, serial_conn)
            time.sleep(0.1)
            subRes = read(serial_conn)
            if subRes == None or subRes == -1:
                # TODO
                errors.append(((UID, delay), subRes))
                continue
            response_UID = subRes.getPayload()[:11]
            response_delay = subRes.getPayload()[11:]
            if UID == response_UID and delay == response_delay:
                pass
            else:
                # TODO
                errors.append(((UID, delay), (response_UID, response_delay)))
        return errors


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
            self._ports[uid] = p


    def _spawnHibikeThread(self):
        pass


# TODO: implement multithreading :)
class HibikeThread():
    def __init__(self, hibike):
        self.hibike = hibike

    def checkSerialPorts(self):
        for port, serial_conn in self.hibike._connections.items():
            msg = read(serial_conn)
            if msg == None or msg == -1:
                continue
            if msg.getMessageID() == messageTypes["DataUpdate"]:
                self.hibike._data[port] = msg.getPayload()

