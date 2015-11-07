import time, random
class Hibike:
    def __init__(self):
        self.UIDs = [
            '0x000000FFFFFFFFFFFFFFFF', '0x000100FFFFFFFFFFFFFFFF',
            '0x000200FFFFFFFFFFFFFFFF', '0x000300FFFFFFFFFFFFFFFF',
            '0x000400FFFFFFFFFFFFFFFF', '0x000500FFFFFFFFFFFFFFFF',
            '0x000600FFFFFFFFFFFFFFFF', '0x000700FFFFFFFFFFFFFFFF',
            '0x000800FFFFFFFFFFFFFFFF'
         ]
        #format Device Type (16) + Year (8) + ones (64)
        self.subscribedto = {}
        self.sensors = []

    def getEnumeratedDevices(self):

        enum_devices = []
        for UID in self.UIDs:
            enum_devices.append((UID, UID[:6])) # (UID - in hex, Device type - in hex)
        return enum_devices

    def subscribeToDevices(self, deviceList):
        for UID, delay in deviceList:
            if UID in self.UIDs and UID not in self.subscribedto:
                last_time = time.time()*1000
                self.subscribedto[UID] = {'delay': delay, 'time': last_time, 'data':(random.random() *100)//1} # (delay, last time sensor data was updated, sensor data)
                self.subscribedto[UID]['flip_time'] = self.calculateFlipTime(UID)
            elif UID in self.UIDs and  UID in self.subscribedto:
                self.subscribedto[UID]['delay'] = delay
        return 0

    def getData(self, UID):
        delay, last_time = self.subscribedto[UID]['delay'], self.subscribedto[UID]['time']
        flip_time = self.subscribedto[UID]['flip_time']
        curr_time = time.time()*1000
        if curr_time - delay >= flip_time:
            self.subscribedto[UID]['time'] = curr_time #updates last time sensor data was updated to current system time
            self.subscribedto[UID]['data'] +=  #rewrites sensor data with random num
        elif curr_time - delay < flip_time and curr_time - delay > last_time:
            self.subscribedto[UID]['time'] = curr_time
            self.subscribedto[UID]['data'] += self.calculateChange(UID, False)
        return self.subscribedto[UID]['data'] #returns sensor data



    def readValue(self, UID, param):
        #param values: 0 - delay, 1 - last_time, 2 - data
        try:
            return self.subscribedto[UID][param]
        except:
            return 1

    def writeValue(self, UID, param, value):
        if param >= len(self.subscribedto[UID]):
            return 1
        self.subscribedto[UID][param] = value
        return 0



    def calculateFlipTime(self, UID):
        random, last_time = random.random(), self.subscribedto[UID]['time']
        noise = random.random()
        for i in range(len(cutoffs)):
            if random < cuttofs[i]:
                return last_time + noise + i

    cutoffs = [0.05, 0.13, 0.15, 0.27, 0.5, 0.73, 0.85, 0.95, 0.99, 1.0]
    sensor_values =


hi = Hibike()
hi.subscribeToDevices([('0x000800FFFFFFFFFFFFFFFF', 1)])
print(hi.subscribedto)
