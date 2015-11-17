import os
import sys
import serial
import binascii
import time
import threading
import struct
import pdb
from Queue import Queue

sys.path.append(os.getcwd())

import hibike_message as hm

class Hibike():
    def __init__(self, context):
        """Enumerate through serial ports with subRequest(0)
        Update self.context as we iterate through with devices
        Build a list self.serialPorts of (uid, port, serial) tuples
        Make context.hibike point to this
        Spawn new thread
        """
        self.context = context
        self.context.hibike = self
        self._portList = self._getPorts()
        self.serialPorts = self._enumerateSerialPorts()
        self.sendBuffer = Queue()
        self.thread = self._spawnHibikeThread()


    def _spawnHibikeThread(self):
        h_thread = HibikeThread(self)
        h_thread.daemon = True
        h_thread.start()
        return h_thread

    def _getPorts(self):
        return ['/dev/%s' % port for port in os.listdir("/dev/") 
                if port[:6] in ("ttyUSB", "tty.us", "ttyACM")]

    #TODO: get rid of locking and change to fit changes!
    def _enumerateSerialPorts(self):
        serialPorts = []
        serial_conns = {p: serial.Serial(p, 115200) for p in self._portList}
        time.sleep(3)

        for p in self._portList:
            serial_conns[p].flushInput()
            hm.send(serial_conns[p], hm.make_sub_request(0))
        time.sleep(2)
        for p in self._portList:
            msg = hm.read(serial_conns[p])
            if msg == None or msg == -1:
                print("read() failed for ping response.")
                continue
            if msg.getmessageID() != hm.messageTypes["SubscriptionResponse"]:
                pdb.set_trace()
                print("wrong message back: "+str(msg))

            res = struct.unpack("<HBQH", msg.getPayload())
            uid = (res[0] << 72) | (res[1] << 64) | (res[2])
            assert uid not in self.context.devices, "UID conflict for id {}".format(uid)
            serialPorts.append((uid, p, serial_conns[p]))
            # self._devices[uid] = hm.getDeviceType(uid)
            # self._data[uid] = 0
            # self._connections[uid] = (p, serial_conns[p])
            self.context._addDeviceToContext(uid)
        return serialPorts

    def getEnumeratedSerialPorts(self):
        return [(val[0], hm.getDeviceType(val[0])) for val in self.serialPorts]

    def _addToBuffer(self, uid, msg):
        filtered = filter(lambda x: x[0] == uid, self.serialPorts)
        if not filtered:
            print "subRequest() failed... uid not in serialPorts"
            return
        _, __, serial = filtered[0]
        self.sendBuffer.put((serial, msg))

    def subRequest(self, uid, delay):
        """Creates packet and adds (serial, packet) to sendBuffer)"""
        msg = hm.make_sub_request(delay)
        self._addToBuffer(uid, msg)


    def deviceUpdate(self, uid, param, value):
        """Creates packet and adds (serial, packet) to sendBuffer)"""
        msg = hm.make_device_update(param, value)
        self._addToBuffer(uid, msg)

    def deviceStatus(self, uid, param):
        """Creates packet and adds (serial, packet) to sendBuffer)"""
        msg = hm.make_device_status(param)
        self._addToBuffer(uid, msg)

    def error(self, error_code):
        msg = hm.make_error(error_code)
        self._addToBuffer(uid, msg)

class HibikeThread(threading.Thread):
    def __init__(self, hibike):
        threading.Thread.__init__(self)
        self.hibike = hibike
        self.serialPortIndex = 0
        self.sendBuffer = hibike.sendBuffer
        self.packets_read = 0

    def run(self):
        while 1:
            self.handleInput(5)
            self.handleOutput(5)


    def handleInput(self, n):
        """Processes a single packet, if one is available, from the next 
        n devices, or the number of devices, whichever is smaller. 

        Where we are in our list of devices is maintained across calls. 

        If n==0, iterate through all devices. 
        """
        numDevices = len(self.hibike.serialPorts)
        if (n == 0):
            n = numDevices
        for _ in range(n):
            serialPort = self.hibike.serialPorts[self.serialPortIndex]
            self.processPacket(serialPort)
            self.serialPortIndex += 1
            self.serialPortIndex %= numDevices


    def processPacket(self, serialPort):
        """Reads a packet from serial, if a packet is available. 

        If a packet is not available, return None.

        Updates corresponding param in context.
        Returns msgID
        """
        uid, port, serial = serialPort

        msg = hm.read(serial)
        if msg == None or msg == -1:
            return None

        msgID = msg.getmessageID()
        if msgID == hm.messageTypes["DataUpdate"]:
            payload = msg.getPayload()
            self.hibike.context._updateParam(uid, 0, payload, time.time())
            
            # testing
            self.packets_read = self.packets_read + 1
            self.hibike.context.log[0].append(time.time())
            self.hibike.context.log[1].append(self.packets_read)
            self.hibike.context.log[2].append(int(binascii.hexlify(payload), 16))
        elif msgID == hm.messageTypes["DeviceResponse"]:
            param, value = struct.unpack("<BI", msg.getPayload())
            self.hibike.context._updateParam(uid, param, value, time.time())
            #self.hibike.context.contextData[uid][0][param] = (value, timestamp)
        elif msgID == hm.messageTypes["SubscriptionResponse"]:
            uid0, uid1, uid2, delay = struct.unpack("<HBQH", msg.getPayload())
            self.hibike.context._updateSubscription(uid, delay, time.time())
        return msgID


    def handleOutput(self, n):
        """Processes the next n packets, or the number of packets, whichever 
        is smaller, in the sendBuffer queue. 

        sendBuffer should have tuples of (serial, packet)
        """

        for _ in range(n):
            if self.sendBuffer.empty():
                break
            serial, packet = self.sendBuffer.get()
            hm.send(serial, packet)




