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
		self._portList = self._getPorts()
        self._enumerateSerialPorts()
        self.thread = self._spawnHibikeThread()


    def _spawnHibikeThread(self):
        h_thread = HibikeThread(self)
        h_thread.daemon = True
        h_thread.start()
        return h_thread


class HibikeThread(threading.Thread):
	def __init__(self, hibike):
		threading.Thread.__init__(self)
        self.hibike = hibike

    def run(self):
        while 1:
            self.handleIntput(x)
            self.handleOutput(y)
