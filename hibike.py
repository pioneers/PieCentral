import os
import sys
import serial
import binascii
import time
import threading
import struct
import pdb

sys.path.append(os.getcwd())

from hibike_message import *

# connections - {uid: (port, Serial)}
# data - {uid, data}
# devices - {uid : devicetype}


class Hibike():

    def __init__(self):
        self._dataLock = threading.Lock()
        self._sendLock = threading.Lock()
        self._readLock = threading.Lock()

        self._portList = self._getPorts()
        self._data = dict()
        self._connections = dict()
        self._devices = dict()

        self._enumerateSerialPorts()
        self._spawnHibikeThread()


    def getEnumeratedDevices(self):
        return self._devices
        #return {self._uids[port]: self._devices[port] for port in self._uids}

    # TODO decide on how to handle failures
    # devices = [(UID, delay)]
    def subToDevices(self, devices):
        errors = []
        for UID, delay in devices:
            payload = bytearray()
            payload.extend(struct.pack("<H", delay))
            subReq = HibikeMessage(messageTypes['SubscriptionRequest'], 
                                    payload)
            serial_conn = self._connections[UID][1]
            send(subReq, serial_conn)
            time.sleep(0.1)

            try:
                self._readLock.acquire()
                subRes = read(serial_conn)
                # pdb.set_trace()
                if subRes == None or subRes == -1:
                    # TODO
                    print("failed with subResponse")
                    errors.append(((UID, delay), subRes))
                    continue
                response_UID = subRes.getPayload()[:11]
                response_delay = subRes.getPayload()[11:]
                if payload == response_delay:
                    pass
                else:
                    # TODO
                    errors.append(((UID, delay), (response_UID, response_delay)))
            
            finally:
                self._readLock.release()
        
        print errors


    # returns the latest device reading, given its uid
    def getData(self, uid):
        try:
            self._dataLock.acquire()
            value = self._data[uid]
        finally:
            self._dataLock.release()
        return value

    def writeValue(self, uid, param, value):
        payload = struct.pack("<BI", param, value)
        send(HibikeMessage(messageTypes['DeviceUpdate'], payload),
            self._connections[uid])
        time.sleep(0.1)
        while(self._connections[uid].inWaiting()):
            curr = read(self._connections[uid])
            if curr.getmessageID() == messageTypes['DeviceResponse']:
                return 0 if (param, value) == struct.unpack("<BI", curr.getPayload()) else 1
        return 1

    def _getPorts(self):
        return ['/dev/%s' % port for port in os.listdir("/dev/") 
                if port[:6] in ("ttyUSB", "tty.us")]


    def _enumerateSerialPorts(self):
        serial_conns = {p: serial.Serial(p, 115200) for p in self._portList}
        payload = bytearray()
        payload.extend(struct.pack("<H", 0))
        pingMsg = HibikeMessage(messageTypes['SubscriptionRequest'], 
                                payload)
        time.sleep(3)

        for p in self._portList:
            send(pingMsg, serial_conns[p])
        time.sleep(0.2)
        for p in self._portList:
            msg = read(serial_conns[p])
            # pdb.set_trace()
            if msg == None or msg == -1:
                print("ping response.")
                continue
            if msg.getmessageID() != messageTypes["SubscriptionResponse"]:
                print("wrong message back: "+str(msg))

            res = struct.unpack("<HBQH", msg.getPayload())
            uid = (res[0] << 72) | (res[1] << 64) | (res[2])
            self._devices[uid] = getDeviceType(uid)
            self._data[uid] = 0
            self._connections[uid] = (p, serial_conns[p])


    def _spawnHibikeThread(self):
        h_thread = HibikeThread(self)
        h_thread.daemon = True
        h_thread.start()


# TODO: implement multithreading :)
class HibikeThread(threading.Thread):
    def __init__(self, hibike):
        threading.Thread.__init__(self)
        self.hibike = hibike
        self.connections = dict(hibike._connections)
        self._dataLock = hibike._dataLock
        self._readLock = hibike._readLock

    def run(self):
        while 1:
            # try:
            self.getDeviceReadings()
            # except:
                # print "Error in Hibike thread."

    def getDeviceReadings(self):
        errors = []
        for uid in self.connections:
            tup = self.connections[uid]

            try:
                self._readLock.acquire()
                mes = read(tup[1])
            finally:
                self._readLock.release()
            
            if mes ==  -1:
                print "Checksum doesn't match"
            #parse the message
            elif mes != None:
                if mes.getmessageID() == messageTypes["DataUpdate"]:
                    try:
                        self._dataLock.acquire()
                        self.hibike._data[uid] = mes.getPayload()
                    finally:
                        self._dataLock.release()
                else:
                    print "Wrong message type sent"
                    print mes

   
    def checkSerialPorts(self):
        for port, serial_conn in self.hibike._connections.items():
            msg = read(serial_conn)
            if msg == None or msg == -1:
                continue
            if msg.getmessageID() == messageTypes["DataUpdate"]:
                self.hibike._data[port] = msg.getPayload()

