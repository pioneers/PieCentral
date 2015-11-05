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
        self._portList = self._getPorts()
        self._connections = dict()
        self._data = dict()
        self._devices = dict()

        self._dataLock = threading.Lock()
        self._serialLock = threading.Lock()
        self._sendQueueLock = threading.Lock()
        
        self._enumerateSerialPorts()
        self.thread = self._spawnHibikeThread()

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

                while currTime - prevTime < timout:
                    subRes = read(serial_conn)
                    currTime = time.time()

                    # Check if read() failed
                    if subRes == None or type(subRes) == int:
                        # TODO: Better error handling (retries+timeout)
                        print("read() failed for subResponse")
                        errors.append(((UID, delay), subRes))
                        continue

                    # Check if read() returned the right type of packet
                    if subRes.getmessageID() == messageTypes["SubscriptionResponse"]:
                        break

                if subRes == None or type(subRes) == int or subRes.getmessageID() != messageTypes["SubscriptionResponse"]:
                    print("read() failed for subResponse entirely")
                    errors.append(((UID, delay), subRes))
                    continue

                payload_tuple = struct.unpack("<HBQH", subRes.getPayload())
                res_uid = (payload_tuple[0] << 72) | (payload_tuple[1] << 64) | (payload_tuple[2])
                res_delay = payload_tuple[3]

                if UID != res_uid or delay != res_delay:
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
                if port[:6] in ("ttyUSB", "tty.us", "ttyACM")]


    def _enumerateSerialPorts(self):
        serial_conns = {p: serial.Serial(p, 115200) for p in self._portList}
        time.sleep(3)

        for p in self._portList:
            serial_conns[p].flushInput()
            send_sub_request(0, serial_conns[p])
        time.sleep(2)
        for p in self._portList:
            msg = read(serial_conns[p])
            if msg == None or msg == -1:
                print("read() failed for ping response.")
                continue
            if msg.getmessageID() != messageTypes["SubscriptionResponse"]:
                pdb.set_trace()
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
        return h_thread


# TODO: implement multithreading :)
class HibikeThread(threading.Thread):
    def __init__(self, hibike):
        threading.Thread.__init__(self)
        self.hibike = hibike
        self.connections = dict(hibike._connections)
        self.writeQueue = list()

        self._dataLock = hibike._dataLock
        self._serialLock = hibike._serialLock
        self._sendQueueLock = hibike._sendQueueLock

    def run(self):
        while 1:
            self.getDeviceReadings()
            self.sendDeviceRequests()

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

   
    def sendDeviceRequests(self):
        timout = 1
        errors = []

        self._sendQueueLock.acquire()
        self._serialLock.acquire()
        try:
            if not self.writeQueue:
                return

            while self.writeQueue:
                msgType, uid, param, val = self.writeQueue.popleft()
                serial_conn = self.connections[uid][0]

                serial_conn.flush()
                send_device_request(msgType, uid, param, val, serial_conn)
                
                prevTime = time.time()
                currTime = prevTime
                time.sleep(0.1)

                while currTime - prevTime < timout:
                    res = read(serial_conn)
                    currTime = time.time()

                    # Check if read() failed
                    if res == None or res == -1:
                        # TODO: Better error handling (retries+timeout)
                        print("read() failed for DeviceRequest")
                        errors.append(((msgType, uid, param, val), res))
                        continue

                    # Check if read() returned the right type of packet
                    if res.getmessageID() == msgType:
                        break

                if subRes == None or type(subRes) == int or subRes.getmessageID() != msgType:
                    print("read() failed for DeviceRequest entirely")
                    errors.append(((msgType, uid, param, val), res))
                    continue

                if msgType == messageTypes["DeviceUpdate"]:
                    res_val = struct.unpack("<I", res.getPayload()[1:])
                    if val != res_val:
                        print("unexpected value back for DeviceUpdate")
                        errors.append(((msgType, uid, param, val), res_val))

                if msgType == messageTypes["DeviceStatus"]:
                    print(str((uid, param, res_val)))


        return errors

        finally:
            self._sendQueueLock.release()
            self._serialLock.release()
