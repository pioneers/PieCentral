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

class Hibike():
	def __init__(self, context):
		self.context = context
		self.connections = []
		self._portList = self._getPorts()
        self._enumerateSerialPorts()

        self.thread = self._spawnHibikeThread()


    def _spawnHibikeThread(self):
        h_thread = HibikeThread(self)
        h_thread.daemon = True
        h_thread.start()
        return h_thread

    #TODO: get rid of locking and change to fit changes!
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

    def run(self):
        while 1:
            self.handleIntput(x)
            self.handleOutput(y)
