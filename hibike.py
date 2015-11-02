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
        self._serialLock = threading.Lock()

        self._portList = self._getPorts()
        self._connections = dict()
        self._data = dict()
        self._devices = dict()

        self._enumerateSerialPorts()
        self._spawnHibikeThread()


    def getEnumeratedDevices(self):
        return self._devices
        #return {self._uids[port]: self._devices[port] for port in self._uids}

    # TODO decide on how to handle failures
    # device_delays = [(UID, delay)]
    def subToDevices(self, device_delays):
        errors = []
        timout = 3      # seconds

        for UID, delay in device_delays:
            serial_conn = self._connections[UID][1]

            try:
                self._serialLock.acquire()

                send_sub_request(delay, serial_conn)
                subRes = None
                time.sleep(0.1)
                prevTime = time.time()
                currTime = prevTime

                while serial_conn.inWaiting() and currTime - prevTime < timout:
                    subRes = read(serial_conn)
                    currTime = time.time()

                    # Check if read() failed
                    if subRes == None or subRes == -1:
                        # TODO: Better error handling (retries+timeout)
                        print("read() failed for subResponse")
                        errors.append(((UID, delay), subRes))
                        continue

                    # Check if read() returned the right type of packet
                    if subRes.getmessageID() == messageTypes["SubscriptionResponse"]:
                        break

                if type(subres) != HibikeMessage or subRes != messageTypes["SubscriptionResponse"]:
                    print("read() failed for subResponse entirely")
                    errors.append((UID, delay), subRes)
                    continue

                res_uid_tuple = struct.unpack("<HBQH", subRes.getPayload()[:11])
                res_uid = (res_uid_tuple[0] << 72) | (res_uid_tuple[1] << 64) | (res_uid_tuple[2])
                res_delay = struct.unpack("<H", subRes.getPayload()[11:])

                if uid != res_uid or delay != res_delay:
                    # TODO: Better error handling (retries+timeout)
                    print("unexpected subResponse values")
                    errors.append(((UID, delay), (res_uid, res_delay)))
            
            finally:
                self._serialLock.release()
        
        print errors


    # returns the latest device reading, given its uid
    # will return None if the data request failed
    def getData(self, uid):
        value = None
        if uid not in self._connections:
            return value

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
        time.sleep(3)

        for p in self._portList:
            send_sub_request(0, serial_conns[p])
        time.sleep(0.2)
        for p in self._portList:
            msg = read(serial_conns[p])
            if msg == None or msg == -1:
                print("read() failed for ping response.")
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
        self._serialLock = hibike._serialLock

    def run(self):
        while 1:
            self.getDeviceReadings()

    def getDeviceReadings(self):
        errors = []
        for uid in self.connections:
            tup = self.connections[uid]

            try:
                self._serialLock.acquire()
                mes = read(tup[1])
            finally:
                self._serialLock.release()
            
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

