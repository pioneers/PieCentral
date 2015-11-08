class DeviceContext():
    def __init__(self, deviceParams):
        #contextData = {uid: {field: (value, timestamp)}, delay, timestamp) } 
        self.contextData = dict()
        self.deviceParams = deviceParams
        self.hibike = None

    def getData(self, uid, param):
        if uid in self.contextData:
            if param in self.contextData[uid]:
                return self.contextData[uid][param]
            else:
                return "The parameter {0} does not exist for your specified device.".format(param)
        else:
            return "You have not specified a valid device. Check your UID."


    def subToDevices(self, deviceTuples):
        for devTup in deviceTuples:
            self.subDevice(uid, delay)

    def subDevice(self, uid, delay):
        assert self.hibike is not None, "DeviceContext needs a pointer to Hibike!"
        self.hibike.sendSubRequest(uid, delay)

    def writeValue(self, uid, param, value):
        assert self.hibike is not None, "DeviceContext needs a pointer to Hibike!"
        assert param in self.deviceParams[getDevice(uid)], "Invalid param for {}".format(getDevice(uid))
        
        self.hibike.sendDeviceUpdate(uid, field, value)

    def getDelay(self, uid):
        if uid in self.contextData:
            return (self.contextData[uid][1], self.contextData[uid][2])
        else:
            return "You have not specified a valid device. Check your UID."
