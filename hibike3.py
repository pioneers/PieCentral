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

from hibike_message

class Hibike():
    def __init__(self, context):
        """Enumerate through serial ports with subRequest(0)
        Update self.context as we iterate through with devices
        Build a list self.serialPorts of (uid, port, serial) tuples
        Make context.hibike point to this
        Spawn new thread
        """
        self.context = context
        self._portList = self._getPorts()
        self.serialPorts = self._enumerateSerialPorts()

        self.thread = self._spawnHibikeThread()


    def _spawnHibikeThread(self):
        h_thread = HibikeThread(self)
        h_thread.daemon = True
        h_thread.start()
        return h_thread

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


class HibikeThread(threading.Thread):
    def __init__(self, hibike):
        threading.Thread.__init__(self)
        self.hibike = hibike
        self.serialPortIndex = 0
        self.sendBuffer = Queue()

    def run(self):
        while 1:
            self.handleInput(x)
            self.handleOutput(y)


    def handleInput(self, n):
        """Processes a single packet, if one is available, from the next 
        n devices, or the number of devices, whichever is smaller. 

        Where we are in our list of devices is maintained across calls. 

        If n==0, set n = numDevices to iterate through all devices. 
        """
        numDevices = len(self.hibike.serialPorts)
        if n==0:
            n = num
        for _ in n:
            serialPort = self.hibike.serialPorts[self.serialPortIndex]
            self.processPacket(serial)
            self.serialPortIndex += 1
            self.serialPortIndex %= numDevices


    def processPacket(self, serialPort):
        """Reads a packet from serial, if a packet is available. 

        If a packet is not available, return None.

        Updates corresponding param in context.
        Returns msgID
        """
        uid, port, serial = serialPort

        msg = hibike_message.read(serial)
        if msg == None or msg == -1:
            return None

        msgID = msg.getmessageID()
        if msgID == hibike_message.messageTypes["DataUpdate"]:
            payload = msg.getPayload()
            self.hibike.context.updateParam(uid, 0, payload, time.time())
        elif msgID == messageTypes["DeviceResponse"]:
            param, value = struct.unpack("<BI", msg.getPayload())
            self.hibike.context.contextData[uid][0][param] = (value, timestamp)
        elif msgID == messageTypes["SubscriptionResponse"]:
            self.hibike.context.updateSubscription(uid, delay, time.time())
        
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
            hibike_message.send(serial, packet)


    def addToBuffer(self, uid, msg):
        filtered = filter(lambda x: x[0] == uid, self.hibike.serialPorts)
        if not filtered:
            print "subRequest() failed... uid not in serialPorts"
            return
        _, __, serial = filtered[0]
        self.sendBuffer.put((serial, msg))

    def subRequest(self, uid, delay):
        """Creates packet and adds (serial, packet) to sendBuffer)"""
        msg = hibike_message.make_sub_request(delay)
        self.addToBuffer(uid, msg)


    def deviceUpdate(self, uid, param, value):
        """Creates packet and adds (serial, packet) to sendBuffer)"""
        msg = hibike_message.make_device_update(param, value)
        self.addToBuffer(uid, msg)

    def deviceStatus(self, uid, param):
        """Creates packet and adds (serial, packet) to sendBuffer)"""
        msg = hibike_message.make_device_status(delay)
        self.addToBuffer(uid, msg)

    def error(self, error_code):
        msg = hibike_message.make_error(error_code)
        self.addToBuffer(uid, msg)

