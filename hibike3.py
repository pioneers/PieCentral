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
        """Enumerate through serial ports with subRequest(0)
        Update self.context as we iterate through with devices
        Build a list self.serialPorts of (uid, port, serial) tuples
        Make context.hibike point to this
        Initialize self.sendBuffer to an empty Queue
        Spawn new thread
        """
        self.context = context
        self._portList = self._getPorts()
        self.serialPorts = self._enumerateSerialPorts()
        self.thread = self._spawnHibikeThread()
        self.sendBuffer = Queue()


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
            self.handleInput(x)
            self.handleOutput(y)


    def handleInput(n):
        """Processes a single packet, if one is available, from the next 
        n devices, or the number of devices, whichever is smaller. 

        Where we are in our list of devices is maintained across calls. 

        If n==0, iterate through all devices. 
        """

    def processPacket(uid):
        """Finds the correct serial port, then reads a packet from it, if 
        a packet is available. 
        If a packet is not available, return None.

        Updates corresponding param in context.
        """

    def updateParam(uid, param, value):
        """Updates the param of the device corresponding with uid to be 
        value, with the timestamp of the current time. 
        """



    def handleOutput(n):
        """Processes the next n packets, or the number of packets, whichever 
        is smaller, in the sendBuffer queue. 

        sendBuffer should have tuples of (serial, packet)
        """

    def subRequest(uid, delay):
        """Creates packet and adds (serial, packet) to sendBuffer)"""
    def deviceUpdate(uid, param, value):
        """Creates packet and adds (serial, packet) to sendBuffer)"""
    def deviceStatus(uid, param):
        """Creates packet and adds (serial, packet) to sendBuffer)"""

