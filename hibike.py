import os
import sys
import serial
import binascii
import time
import threading

sys.path.append(os.getcwd())

from hibike_message import *

# connections - {uid: (port, Serial)}
# data - {uid, data}
# devices - {uid : devicetype}


class Hibike():
    def __init__(self):
        self._data = dict()
        self._connections = dict()
        self._devices = dict()

        self._enumerateSerialPorts()


    def getEnumeratedDevices(self):
        return self._devices
        #return {self._uids[port]: self._devices[port] for port in self._uids}

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


    # returns the latest device reading, given its uid
    # Liza: not sure if we still want to keep the access via port, since each uid is anyway mapped to the (port, Serial) tuple
    def getData(self, uid):
        return self._data[uid]

    def writeData(self, port):
        raise NotImplementedError

    def _getPorts(self):
        return ['/dev/%s' % port for port in os.listdir("/dev/") 
                if port[:6] == "ttyUSB"]

    def _getDeviceReadings(self):
        errors = []
        for uid in self._connections:
            tup = self._connections[uid]
            mes = read(tup[1])
            if mes ==  -1:
                print "Checksum doesn't match"
            #parse the message
            else if mes != None:
                if mes.getMessageID() == messageTypes["DataUpdate"]:
                    data[uid] = mes.getPayload()
                else:
                    print "Wrong message type sent"


    def _enumerateSerialPorts(self):
        ports = self._getPorts()
        serial_conns = {p: serial.Serial(p, 115200) for p in ports}
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
        h_thread = HibikeThread(self)
        h_thread.start()


# TODO: implement multithreading :)
class HibikeThread(threading.Thread):
    def __init__(self, hibike):
        threading.Thread.__init__(self)
        self.hibike = hibike

    def run(self):
        while 1:
            try:
                hibike._getDeviceReadings()
            except:
                print "Error in Hibike thread."


    def checkSerialPorts(self):
        for port, serial_conn in self.hibike._connections.items():
            msg = read(serial_conn)
            if msg == None or msg == -1:
                continue
            if msg.getMessageID() == messageTypes["DataUpdate"]:
                self.hibike._data[port] = msg.getPayload()

