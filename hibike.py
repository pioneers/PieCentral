from __future__ import print_function
import os
import sys
import serial
import serial.tools.list_ports as serialtools
import binascii
import time
import threading
import struct
import pdb
import random
from collections import namedtuple, OrderedDict
from threading import Timer
try:
    from Queue import Queue, Full
except ImportError:
    from queue import Queue, Full
import csv
import json
import pdb

sys.path.append(os.getcwd())

import hibike_message as hm

# Global meta variables
smartDeviceBoards = ['Sparkfun Pro Micro', 'Intel Corp. None ', 'ttyACM0', 'ttyACM2']


class Hibike():
    def __init__(self, contextFile=os.path.join(os.path.dirname(__file__), 'hibikeDevices.json'), timeout=5.0, maxsize=100):
        """Enumerate through serial ports with subRequest(0)
        Update self.context as we iterate through with devices
        Build a list self.serialPorts of (uid, port, serial) tuples
        Make context.hibike point to this
        Spawn new thread
        """
        self.config = {}          # {deviceType: {"deviceName": deviceName, paramName: paramID}}
        self.deviceTypes = {}     # {deviceType: DeviceType}
        self.deviceTypeFragments = {}
        self.context = {}         # {uid: contextObj}
        self.uidToSerial = {}     # {uid: serPort}
        self.serialToUID = {}     # {serPort: (uid, serialObj)}
        self.timeout = timeout
        self.sendBuffer = Queue(maxsize=maxsize)
        self._readContextFile(contextFile)
        self.thread = self._spawnHibikeThread()
        self._enumerateSerialPorts()
        self.contextFile = contextFile
        time.sleep(self.timeout*1.5)

    def __str__(self):
        """
        Devices:
        """
        hibike_str = "Hibike:\n"
        hibike_str += "  Ports:\n"
        for port in self.serialToUID.keys():
            hibike_str += "    %s\n" % port
        hibike_str += "  Devices:\n"
        for device in self.context.values():
            hibike_str += "    %s\n" % device
        return hibike_str

    def __repr__(self):
        return self.__str__()

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
        try:
            csv_file = None
            json_file = None
            ext = os.path.splitext(contextFile)[1]
            if  ext == '.csv':
                csv_file = open(contextFile, 'r')
                reader = csv.reader(csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                list_of_rows = [row for row in reader]
                list_of_rows.pop(0)
                for row in list_of_rows:
                    self.deviceTypes[int(row[0], 16)] = DeviceType(row, 'csv')
            elif ext == '.json':
                json_file = open(contextFile, 'r')
                def as_device(dct):
                    if 'deviceID' in dct:
                        return DeviceType(dct, 'json')
                    else:
                        return dct
                json_deviceTypes = json.load(json_file, object_hook=as_device)
                self.deviceTypes = {deviceType.deviceID: deviceType for deviceType in json_deviceTypes['devices']}
            else:
                print("Bad Config: config file must be .csv or .json")
        except IOError:
            print("ERROR: Hibike config filed does not exist.")
        finally:
            if csv_file is not None:
                csv_file.close()
            if json_file is not None:
                json_file.close()

    def _updateContextFile(self, contextFile, newDeviceType):
        try:
            csv_file = None
            json_file = None
            ext = os.path.splitext(contextFile)[1]
            if  ext == '.csv':
                raise NotImplementedError
            elif ext == '.json':
                new_json = json.loads(newDeviceType.to_json(), object_pairs_hook=OrderedDict)
                json_file = open(contextFile, 'r')
                json_deviceTypes = json.load(json_file, object_pairs_hook=OrderedDict)
                json_file.close()
                json_file = open(contextFile, 'w')
                json_deviceTypes['devices'].append(new_json)
                json_deviceTypes['devices'].sort(key=lambda deviceType: int(deviceType["deviceID"], 16))
                json.dump(json_deviceTypes, json_file, indent=4, separators=(',', ': '))
                json_file.close()
            else:
                print("Bad Config: config file must be .csv or .json")
        except IOError as e:
            print("ERROR: Hibike config file does not exist: ", e)
        finally:
            if csv_file is not None:
                csv_file.close()
            if json_file is not None:
                json_file.close()


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
        portInfo = serialtools.grep('ttyACM')
        for ser, desc, hwid in portInfo:
            try:
                delay = 0
                if ser in self.serialToUID.keys():
                    uid = self.serialToUID[ser][0]
                    if uid in self.context.keys():
                        delay = self.context[uid].delay
                else:
                    self.serialToUID[ser] = (None, serial.Serial(ser, 115200))
                #msg = hm.make_sub_request(delay)
                #print("enumerating something")
                try:
                    self.sendBuffer.put((self.serialToUID[ser][1], hm.make_ping()), block=False)
                except Full:
                    print("QUEUE FULL!!! FLUSHING")
                    self.sendBuffer.queue.clear()
                #hm.send(self.serialToUID[ser][1], msg)
            except (serial.serialutil.SerialException, OSError):
                pass
            except:
                print("Unexpected error", sys.exc_info()[0])
        t = Timer(self.timeout, self._enumerateSerialPorts)
        t.start()


    def _cleanSerialPorts(self):
        """Removes all devices from self.context that are stale.
        A device is stale if its subscription delay was last updated longer 
        thatn self.timeout ago. 
        Enumerates serial ports again when finished. 
        """
        return
        curTime = time.time()
        for uid in self.getUIDs():
            if self.context[uid].lastUpdate + 1.5*self.timeout < curTime:
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
    def getData(self, uid, param, data_format='dict'):
        """Returns the data associated with param of device with uid 
        Returns None if bad uid or bad param
        """
        if uid not in self.getUIDs():
            print("Bad UID")
            return None
        if type(param) is str:
            if param not in self.deviceTypes[self.getDeviceType(uid)]:
                print("Bad param")
                return None
            param = self.deviceTypes[self.getDeviceType(uid)].paramIDs[param]
        return self.context[uid].getData(param, data_format)


    def getDeviceName(self, deviceType):
        """Returns the name of the device associated with deviceType 
        """
        if deviceType not in self.deviceTypes:
            print("Bad deviceType of uid")
            return None
        return self.deviceTypes[deviceType].deviceName


    def getDelay(self, uid):
        """Gets the delay rate for the specified uid 
        Returns None if bad uid 
        """
        if uid not in self.getUIDs():
            print("Bad UID")
            return None
        return self.context[uid].delay


    def getParams(self, uid):
        """Returns a list of strings for all parameter names of the 
        specified uid. 
        Returns none if deviceType of uid is invalid 
        """
        deviceType = self.getDeviceType(uid)
        if deviceType not in self.deviceTypes:
            print("Bad deviceType of uid")
            return None
        params = self.deviceTypes[deviceType].params
        return params


    def writeValue(self, uid, param, value):
        """Writes a value to the parameter of a particular device, 
        specified by uid
        """
        if uid not in self.getUIDs():
            print("Bad UID")
            return None
        if type(param) is str:
            if param not in self.deviceTypes[self.getDeviceType(uid)]:
                print("Bad param")
                return None
            param = self.deviceTypes[self.getDeviceType(uid)].paramIDs[param]
        self.deviceUpdate(uid, param, value)

    def readValue(self, uid, param):
        """Writes a value to the parameter of a particular device, 
        specified by uid
        """
        if uid not in self.getUIDs():
            print("Bad UID")
            return None
        if type(param) is str:
            if param not in self.deviceTypes[self.getDeviceType(uid)]:
                print("Bad param")
                return None
            param = self.deviceTypes[self.getDeviceType(uid)].paramIDs[param]
        self.deviceStatus(uid, param)


    def subToDevice(self, uid, delay):
        """Subscribes to the specified uid with the given delay. 
        Returns None if bad uid
        Otherwise returns delay
        """
        if uid not in self.getUIDs():
            print("Bad UID")
            return None
        self.subRequest(uid, delay)
        return delay


    def subToDevices(self, deviceTuples):
        """Subscribes to a list of (uid, delay) tuples. Will fail if 
        any uid has not been found. 
        Returns 1 on success
        """
        uids = self.getUIDs()
        for device in deviceTuples:
            if device[0] not in uids:
                print("Bad uid")
                return None
        for device in deviceTuples:
            self.subToDevice(device[0], device[1])
        return 1


    def _addToBuffer(self, uid, msg):
        """Returns the msgID if successful, None otherwise 
        """
        if uid not in self.getUIDs():
            print("subRequest() failed... uid not in serialPorts")
            return None
        try:         
            self.sendBuffer.put((self.serialToUID[self.uidToSerial[uid]][1], msg), block=False)
        except Full:
            print("QUEUE FULL!!! FLUSHING")
            self.sendBuffer.queue.clear()
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


    def error(self, uid, error_code):
        msg = hm.make_error(error_code)
        self._addToBuffer(uid, msg)

    def ping(self, uid):
        msg = hm.make_ping()
        self._addToBuffer(uid, msg)

    def descriptionRequest(self, uid):
        msg = hm.make_description_request()
        self._addToBuffer(uid, msg)



class HibikeThread(threading.Thread):
    def __init__(self, hibike):
        threading.Thread.__init__(self)
        self.hibike = hibike
        self.context = self.hibike.context
        self.sendBuffer = hibike.sendBuffer
        self.packets_read = 0


    def run(self):
        # TODO
        # Optimize to only wake on something triggering
        while 1:
            self.handleInput(5)
            self.handleOutput(20)
            time.sleep(0.001)

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
        if not self.hibike.serialToUID:
            return
        randIter = self.hibike.serialToUID.keys()
        random.shuffle(randIter)
        for serialPort in randIter:
            packet = self.processPacket(serialPort)
            if packet:
                counter += 1
            if counter >= n:
                break


    def processPacket(self, serialPort):
        """Reads a packet from serial, if a packet is available. 

        If a packet is not available, return None.

        Updates corresponding param in context.
        Returns msgID
        """
        uid, serial = self.hibike.serialToUID[serialPort]
        if serial == None:
            return
        #print(serial)
        try:
            msg = hm.read(serial)
        except IOError:
            #denumerate the port
            if uid:
                del self.hibike.context[uid]
                del self.hibike.uidToSerial[uid]
            del self.hibike.serialToUID[serialPort]
            return
        if msg == None or msg == -1:
            #print(serial)
            return None
        msgID = msg.getmessageID()
        if msgID == hm.messageTypes["DataUpdate"]:
            if uid in self.context:
                payload = msg.getPayload()
                self.hibike.context[uid].dataUpdate(payload)            
        elif msgID == hm.messageTypes["DeviceResponse"]:
            if uid in self.context and len(msg.getPayload()) == 5:
                param, value = struct.unpack("<BI", msg.getPayload())
                self.hibike.context[uid].deviceResponse(param, value)
        elif msgID == hm.messageTypes["SubscriptionResponse"]:
            if len(msg.getPayload()) == 13:
                deviceType, year, ID, delay = struct.unpack("<HBQH", msg.getPayload())
                #print(deviceType, year, ID, delay)
                uid = (deviceType << 72) | (year << 64) | ID
                cur_ser = self.hibike.uidToSerial.get(uid, None)
                if cur_ser and cur_ser != serialPort:
                    print("UID CONFLICT!!!")
                self.hibike.serialToUID[serialPort] = (uid, serial)
                self.hibike.uidToSerial[uid] = serialPort

                if uid not in self.context:
                    if deviceType not in self.hibike.deviceTypes:
                        print("Unknown Device Type: %s" % (str(deviceType),))
                        try:
                            self.sendBuffer.put((self.hibike.serialToUID[serialPort][1], hm.make_description_request()), block=False)
                            self.hibike.deviceTypeFragments[uid] = {}
                        except Full:
                            print("Queue Full!")
                        #self.hibike.descriptionRequest(uid)
                        return msgID
                    self.context[uid] = HibikeDevice(uid, self.hibike.deviceTypes[deviceType])
                self.context[uid].updateDelay(delay)
        # reassembles fragmented descriptor string
        elif msgID == hm.messageTypes["DescriptionResponse"]:
            index, data = msg.getPayload()[:1], msg.getPayload()[1:]
            (index, )= struct.unpack("<B", index)
            typeDict = self.hibike.deviceTypeFragments[uid]
            typeDict[index] = str(data)
            if '\x00' in data:
                typeDict[-1] = index + 1
            if -1 in typeDict:
                fullDescriptor = '';
                for i in range(typeDict[-1]):
                    if i in typeDict:
                        fullDescriptor += typeDict[i]
                    else:
                        print("failed to get descriptor: packets dropped")
                        break
                else:
                    fullDescriptor = fullDescriptor[:-1]
                    #print("descriptor:", fullDescriptor)
                    try:
                        newDeviceType = DeviceType(fullDescriptor, 'json', True)
                    except:
                        print("Bad descriptor:", fullDescriptor)
                    else:
                        self.hibike.deviceTypes[newDeviceType.deviceID] = newDeviceType
                        print("new device type:")
                        print(newDeviceType)
                        self.context[uid] = HibikeDevice(uid, newDeviceType)
                        self.hibike._updateContextFile(self.hibike.contextFile, newDeviceType)
        else:
            print("Unexpected message type received")
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

class DeviceType():
    """Not exposed to the user.
    Class used to represent device types internally
    """

    def __init__(self, config, config_format, string=False):
        if config_format == 'json':
            json_dict           = json.loads(config) if string else config
            self.deviceID       = int(str(json_dict["deviceID"]), 16)
            self.deviceName     = str(json_dict["deviceName"])
            self.dataFormat     = str(json_dict["dataFormat"]["formatString"])
            struct.calcsize(self.dataFormat)
            parameters          = json_dict["dataFormat"]["parameters"]
            self.scalingFactors = [float(param['scalingFactor']) for param in parameters]
            self.machineNames   = [str(param['machineName']) for param in parameters]
            self.humanNames     = [str(param['humanName']) for param in parameters]
            self.dataTuple      = namedtuple(self.deviceName, self.machineNames)
            self.params         = map(str, json_dict["params"])
            self.paramIDs       = {self.params[index]: index for index in range(len(self.params))}
        else:
            csv_row             = csv.reader(
                [description], delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL
                ).next() if string else config
            self.deviceID       = int(csv_row[0], 16)
            self.deviceName     = csv_row[1]
            self.dataFormat     = csv_row[2]
            self.scalingFactors = [float(item.strip()) for item in csv_row[3].split(",") if item.strip()]
            self.machineNames   = [item.strip() for item in csv_row[4].split(",") if item.strip()]
            self.humanNames     = [item.strip() for item in csv_row[5].split(",") if item.strip()]
            self.dataTuple      = namedtuple(self.deviceName, self.machineNames)
            self.params         = [param for param in csv_row[6:] if param != '']
            self.paramIDs       = {self.params[index]: index for index in range(len(self.params))}

    def __contains__(self, item):
        return item < len(self.params) or item in self.paramIDs

    def __str__(self):
        deviceType = "DeviceType 0x%04x: %s\n" % (self.deviceID, self.deviceName)
        deviceType += "  Data Format:\n"
        deviceType += "    '%s'\n    %s\n    %s\n    %s\n" % (self.dataFormat, self.scalingFactors, self.machineNames, self.humanNames)
        deviceType += "  Params:\n"
        deviceType += "\n".join(["    %s" % param for param in self.params])
        return deviceType

    def dict_factory(self, *values):
        return {field: value for field, value in zip(self.machineNames, values)}

    def to_csv(self):
        return '0x%x,%s,"%s","%s","%s",%s' % (
            self.deviceID, self.deviceName, self.dataFormat, ',',join(self.scalingFactors),
            ',',join(self.machineNames), ',',join(self.humanNames), ','.join(self.params)
            )

    def to_json(self):
        deviceTypeDict = OrderedDict()
        deviceTypeDict["deviceID"] = "0x%04X" % self.deviceID
        deviceTypeDict["deviceName"] = self.deviceName
        deviceTypeDict["dataFormat"] = OrderedDict()
        deviceTypeDict["dataFormat"]["formatString"] = self.dataFormat
        deviceTypeDict["dataFormat"]["parameters"] = [OrderedDict([("scalingFactor", s), ("machineName", m), ("humanName", h)]) for s, m, h in zip(self.scalingFactors, self.machineNames, self.humanNames)]
        deviceTypeDict["params"] = self.params
        return json.dumps(deviceTypeDict)


class HibikeDevice:
    """Not exposed to the user. 
    Class used to represent devices internally 
    """
    def __init__(self, deviceID, deviceType):
        self.delay = 0
        self.lastUpdate = 0
        self.deviceType = deviceType
        emptyDataUpdate = bytearray([0] * struct.calcsize(self.deviceType.dataFormat))
        self.params = [(emptyDataUpdate, -1)] + [(0, -1)]*(len(deviceType.params) - 1)
        self.deviceID = deviceID

    def __str__(self):
        deviceStr  = "Device 0x%011x: %s\n" % (self.deviceID
            , self.deviceType.deviceName)
        deviceStr += "    subcription: %dms @ %f\n" % (self.delay
            , self.lastUpdate)
        for i in range(len(self.params)):
            value = self.getData(i, 'dict')
            if type(value) in (str, bytes, bytearray):
                value = binascii.hexlify(value)
            else:
                value = str(value)
            deviceStr += "    %s: %s @ %f\n" % (self.deviceType.params[i]
                , value, self.params[i][1])
        return deviceStr

    def updateDelay(self, delay):
        """Updates delay of this subscription to delay
        """
        self.delay = delay
        self.lastUpdate = time.time()


    def dataUpdate(self, payload):
        self.params[0] = (payload, time.time())


    def deviceResponse(self, param, value):
        self.params[param] = (value, time.time())

    # converts dataupdate from bytearray to specified format
    def getData(self, param, data_format="tuple"):
        formats = {"dict": self.dataToDict, "tuple": self.dataToTuple, "int": self.dataToInt}
        data = self.params[param]
        if param == 0:
            data = (formats[data_format](data), self.params[param][1])
        return data

    def dataToDict(self, data):
        unpacked = struct.unpack(self.deviceType.dataFormat, data)
        scaled = [field / scale if scale != 1 else field for field, scale in zip(unpacked, self.deviceType.scalingFactors)]
        return self.deviceType.dict_factory(*scaled)

    def dataToTuple(self, data):
        unpacked = struct.unpack(self.deviceType.dataFormat, data)
        scaled = [field / scale if scale != 1 else field for field, scale in zip(unpacked, self.deviceType.scalingFactors)]
        return tuple(scaled)


    def dataToInt(self, data):
        total = 0
        for byte in list(bytearray(data)):
            total = (total << 8) | byte
        return total
