import time, random

cutoffs = [0.05, 0.13, 0.15, 0.27, 0.5, 0.73, 0.85, 0.95, 0.99, 1.0]
sensor_values = {
    '0x0000': (0, 1, 0),
    '0x0001': (200, 800, 100),
    '0x0002': (None, None, None),
    '0x0003': (-256, 256, 10),
    '0x0004': (0, 1, 0),
    '0x0005': (0, 1, 0),
    '0x0006': (None, None, None),
    '0x0007': (None, None, None),
    '0x0008': (None, None, None)
}

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
                self.subscribedto[UID] = {'delay': delay, 'time': last_time, 'data': self.getRandomData(UID, 0, False)} # (delay, last time sensor data was updated, sensor data)
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
            self.subscribedto[UID]['data'] =  self.getRandomData(UID, 0, True)#rewrites sensor data with random num
            self.subscribedto[UID]['flip_time'] = self.calculateFlipTime(UID)
        elif curr_time - delay < flip_time and curr_time - delay > last_time:
            self.subscribedto[UID]['time'] = curr_time
            self.subscribedto[UID]['data'] = self.getRandomData(UID, self.subscribedto[UID]['data'], False)
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
        rand, last_time = random.random(), self.subscribedto[UID]['time']
        noise = random.random()
        for i in range(len(cutoffs)):
            if rand < cutoffs[i]:
                return time.time() + noise + i



    def getRandomData(self, UID, current_data, flip):
        device_type = UID[:6]
        low, high, noise = sensor_values[device_type]
        average = (low + high) / 2
        if current_data < average:
            if flip:
                return high + (random.random() - .5) * noise
            else:
                return low + (random.random() - .5) * noise
        else:
            if flip:
                return low + (random.random() - .5) * noise
            else:
                return high + (random.random() - .5) * noise



hi = Hibike()
hi.subscribeToDevices([('0x000100FFFFFFFFFFFFFFFF', 1)])
print(hi.subscribedto)
