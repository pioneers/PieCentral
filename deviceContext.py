import hibike_message as hm
import csv

class Device():
    # [{param: (value, timestamp)}, delay, timestamp]
    # NOT TOUCHED BY USER?!
    # user
    def __init__(self):
        # string name to param id, param to string name
        self.params =
        self.delay =
        self.timestamp =
        self.nameToID = {paramName: paramID} # <in a different config file, indexed [???]>
        self.IDToName = {paramID: paramName}


class DeviceContext():
    def __init__(self, configFile='hibikeDevices.csv'):
        # contextData = {uid: Device() }
        self.contextData = dict()
        self.deviceParams = dict()
        self.version = None
        self.hibike = None
        self.readConfig(configFile)


    def readConfig(self, filename):
        """
        Read the configuration information given in 'filename'
        Handle all IO Exceptions
        Fill out self.deviceParams and self.version

        Config file format:
        deviceID1, deviceName1, param1, param2, ...
        deviceID2, deviceName2, param1, param2, ...

        self.deviceParams format:
        self.deviceParams = {deviceID : (param1, param2, ...)}

        self.version format:
        self.version = <string repr of version info>
        """
        try:
            csv_file = open(filename, 'r')
            reader = csv.reader(csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            list_of_rows = [row for row in reader]
            list_of_rows.pop(0)
            self.deviceParams = {int(lst[0], 16): [elem for elem in lst[2:] if elem != ''] for lst in list_of_rows}
        except IOError:
            return "The file does not exist."
        finally:
            csv_file.close()

    def addDeviceToContext(self, uid):
        """
        Add given device to self.contextData, adding params specified
        by self.deviceParams based on the UID
        Handle invalid UIDs
        """

    def getData(self, uid, param):
        """
        Gets device that corresponds to UID
        Gets deviceType
        Gets paramID corresponding to param for that type
        Queries Device w/ that paramID
        Returns that parameter
        """
        if uid in self.contextData:
            if param in self.contextData[uid]:
                return self.contextData[uid][param]
            else:
                return "The parameter {0} does not exist for your specified device.".format(param)
        else:
            return "You have not specified a valid device. Check your UID."

    def updateParam(self, UID, paramID, value, timestamp): # Hibike calling this?
        """
        Get Device
        If timestamp given > timestamp original, replace old tuple with new value & timestamp
        """


    def subToDevices(self, deviceTuples):
        for devTup in deviceTuples:
            self.subDevice(uid, delay)

    def subDevice(self, uid, delay):
        assert self.hibike is not None, "DeviceContext needs a pointer to Hibike!"
        assert uid in self.contextData, "Invalid UID: {}".format(uid)
        assert 0 <= delay < 65535, "Invalid delay: {}".format(delay)

        msg = hm.make_sub_request(uid, delay)
        self.hibike.sendBuffer.put((msg, self.hibike.connections[uid][1]))

    def writeValue(self, uid, param, value):
        assert self.hibike is not None, "DeviceContext needs a pointer to Hibike!"
        assert uid in self.contextData, "Invalid UID: {}".format(uid)
        assert param in self.deviceParams[hm.getDeviceType(uid)], "Invalid param for {}".format(hm.getDeviceType(uid))

        msg = hm.make_device_update(param, value)
        self.hibike.sendBuffer.put((msg, self.hibike.connections[uid][1]))

    def getDelay(self, uid):
        if uid in self.contextData:
            return (self.contextData[uid][1], self.contextData[uid][2])
        else:
            return "You have not specified a valid device. Check your UID."
