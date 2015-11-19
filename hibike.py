import os
import sys
import serial
import serial.tools.list_ports
import binascii
import time
import threading
import struct
import pdb
import random
from Queue import Queue

sys.path.append(os.getcwd())

import hibike_message as hm

# Global meta variables
smartDeviceBoards = ['Sparkfun Pro Micro']


class Hibike():
    def __init__(self, contextFile, timeout=5.0):
        """Enumerate through serial ports with subRequest(0)
        Update self.context as we iterate through with devices
        Build a list self.serialPorts of (uid, port, serial) tuples
        Make context.hibike point to this
        Spawn new thread
        """
        self.config = self._readContextFile(contextFile)
        self.context = {}
        self.uidToSerial = {}
        self.serialToUID = {}
        self.timeout = timeout
        self.sendBuffer = Queue()
        
        self.thread = self._spawnHibikeThread()
        self._enumerateSerialPorts()
        time.sleep(self.timeout*1.5)


    def _readContextFile(self, contextFile):
        """contextFile is the name to a csv containing information of devices 
        deviceID, deviceName, param0, param1, ...
        paramX are the names of the parameters that the user refers to 
        param0 is always "dataUpdate", and is updated via subscription 
        We need to map every param name to a param value
        This implies a dictionary of dictionaries. The first dictionary is 
        keyed on deviceID. 
        The second dictionary is keyed on paramX, value as X, and has an 
        additional (key, value) pair of ("deviceName", deviceName)
        """
        raise NotImplementedError("_readContextFile not implemented")
        try:
            csv_file = open(contextFile, 'r')
            reader = csv.reader(csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            list_of_rows = [row for row in reader]
            list_of_rows.pop(0)
            for row in list_of_rows:
                self.config[row[0]] = {row[i]:i-2 for i in range(len(row))[2:]}
                self.config[row[0]]["deviceName"] = row[1]
        except IOError:
            return "The file does not exist."
        finally:
            csv_file.close()


    def _enumerateSerialPorts(self):
        """Enumerates all devices that have a Smart Device attached. 
        Correct ports are identified by matching to port descriptors 
        contained in smartDeviceBoards. 
        Sub responses will be caught by HibikeThread
        If devices are dropping and reconnecting too often, consider sending 
        the sub request and sub response messages multiple times. 
        #TODO any device that is no longer enumerated should be assumed 
        unplugged, and either removed from self.serialPorts, or a flag set 
        to denote that said device is no longer valid.

        """
        portInfo = serial.tools.list_ports.comport()
        for serial, desc, hwid in portInfo:
            if desc in smartDeviceBoards:
                msg = hm.make_sub_request(0)
                hm.send(serial, msg)
        t = timer(self.timeout, _cleanSerialPorts)
        t.start()


    def _cleanSerialPorts(self):
        """Removes all devices from self.context that are stale.
        A device is stale if its subscription delay was last updated longer 
        thatn self.timeout ago. 
        Enumerates serial ports again when finished. 
        """
        curTime = time.time()
        for uid in self.getUIDs():
            if self.context[uid].lastUpdate + self.timeout < curTime:
                del self.context[uid]
        self._enumerateSerialPorts()



    def _spawnHibikeThread(self):
        h_thread = HibikeThread(self)
        h_thread.daemon = True
        h_thread.start()
        return h_thread


    def getUIDs(self):
        """Returns a list of UID's of all current enumerated devices 
        """
        return self.context.keys()


    def getDeviceType(self, uid):
        """Returns the devicetype of a given UID 
        """
        return uid >> 72


    def getEnumeratedDevices(self):
        return [(uid, self.getDeviceType(uid)) for uid in self.getUIDs()]
    def getData(self, uid, param): 
        """Returns the data associated with param of device with uid 
        Returns None if bad uid or bad param
        """
        if uid not in self.getUids():
            print "Bad UID"
            return None
        if param not in self.config[self.getDeviceType(uid)].keys():
            print "Bad param"
            return None
        paramIndex = self.config[self.getDeviceType(uid)][param]
        return self.context[uid].getData(self.config[)


    def getDeviceName(self, devicetype):
        """Returns the name of the device associated with deviceType 
        """
        if deviceType not in self.config.keys():
            print "Bad deviceType of uid"
            return None
        return self.config[deviceType]["deviceName"]


    def getDelay(self, uid):
        """Gets the delay rate for the specified uid 
        Returns None if bad uid 
        """
        if uid not in self.getUids():
            print "Bad UID"
            return None
        return self.context[uid].delay


    def getParams(self, uid):
        """Returns a list of strings for all parameter names of the 
        specified uid. 
        Returns none if deviceType of uid is invalid 
        """
        deviceType = self.getDeviceType(uid)
        if deviceType not in self.config.keys():
            print "Bad deviceType of uid"
            return None
        params = self.config[deviceType].keys()
        params.remove["deviceName"]
        return params


    def writeValue(self, uid, param, value):
        """Writes a value to the parameter of a particular device, 
        specified by uid
        """
        if uid not in self.getUids():
            print "Bad UID"
            return None
        if param not in self.config[self.getDeviceType(uid)].keys():
            print "Bad param"
            return None
        paramIndex = self.config[self.getDeviceType(uid)].keys()
        self.deviceUpdate(uid, param, value)


    def subToDevice(uid, delay):
        """Subscribes to the specified uid with the given delay. 
        Returns None if bad uid
        Otherwise returns delay
        """
        if uid not in self.getUids():
            print "Bad UID"
            return None
        self.subRequest(uid, delay)
        return delay


    def subToDevices(deviceTuples):
        """Subscribes to a list of (uid, delay) tuples. Will fail if 
        any uid has not been found. 
        Returns 1 on success
        """
        uids = self.getUIDs()
        for device in deviceTuples:
            if device[0] not in uids:
                print "Bad uid"
                return None
        for device in deviceTuples:
            subToDevice(device[0], device[1])
        return 1


    def _addToBuffer(self, uid, msg):
        """Returns the msgID if successful, None otherwise 
        """
        if uid not in self.getUIDs():
            print "subRequest() failed... uid not in serialPorts"
            return None            
        self.sendBuffer.put((self.uidToSerial[uid], msg))
        return msg.getmessageID()


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
        self.sendBuffer = hibike.sendBuffer
        self.packets_read = 0


    def run(self):
        # TODO
        # Optimize to only wake on something triggering
        while 1:
            self.handleInput(5)
            self.handleOutput(5)


    def handleInput(self, n):
        """Processes a single packet, if one is available, from the next 
        n devices, or the number of devices, whichever is smaller. 

        Which device we service next is determined randomly. On average, 
        this should work. 

        If n==0, iterate through all devices. 
        """
        numDevices = len(self.hibike.getUIDs())
        if (n == 0):
            n = numDevices
        counter = 0
        for serial in random.shuffle(self.hibike.serialToUID.keys()):
            packet = self.processPacket(serial)
            if packet:
                counter += 1
            if counter >= n:
                break


    def processPacket(self, serial):
        """Reads a packet from serial, if a packet is available. 

        If a packet is not available, return None.

        Updates corresponding param in context.
        Returns msgID
        """
        uid = self.hibike.serialToUID[serial]

        msg = hm.read(serial)
        if msg == None or msg == -1:
            return None

        msgID = msg.getmessageID()
        if msgID == hm.messageTypes["DataUpdate"]:
            payload = msg.getPayload()
            self.hibike.context[uid].dataUpdate(payload)            
        elif msgID == hm.messageTypes["DeviceResponse"]:
            param, value = struct.unpack("<BI", msg.getPayload())
            self.hibike.context[uid].deviceResponse(param, value)
        elif msgID == hm.messageTypes["SubscriptionResponse"]:
            deviceType, year, ID, delay = struct.unpack("<HBQH", msg.getPayload())
            uid = deviceType << 72 + year << 64 + ID

            self.serialToUID[serialPort] = uid
            self.uidToSerial[uid] = serialPort

            if uid not in self.context.keys():
                if deviceType not in self.config.keys():
                    print "Unknown Device Type: %s" % (str(deviceType),)
                    return msgID
                self.context[uid] = HibikeDevice(deviceType, self.config[deviceType]['deviceName'], len(self.config[deviceType])-1)
            self.context[uid].updateDelay(delay)
        else:
            print "Unexpected message type received"
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


class HibikeDevice:
    """Not exposed to the user. 
    Class used to represent devices internally 
    """
    def __init__(self, deviceID, deviceName, numParams):
        self.delay = 0
        self.lastUpdate = 0
        self.params = [0]*numParams
        self.deviceName = deviceName
        self.deviceID = deviceID


    def updateDelay(self, delay):
        """Updates delay of this subscription to delay
        """
        self.delay = delay
        self.lastUpdate = time.time()


    def dataUpdate(self, payload):
        self.params[0] = (payload, time.time())


    def deviceResponse(self, param, value):
        self.params[param] = value

    def getData(self, param):
        return self.params[param][0]