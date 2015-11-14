import time, random

#weight of each time interval for flipping.
#for example, there is a 5% chance the data will flip within 1 sec
cutoffs = [0.05, 0.13, 0.15, 0.27, 0.5, 0.73, 0.85, 0.95, 0.99, 1.0]

# Sensor type: (low value, high value, noise)
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
        self.subscribedTo = {}
        self.sensors = []


    def getEnumeratedDevices(self):
        """ Returns a list of tuples of UIDs and device types. """

        enum_devices = []
        for UID in self.UIDs:
            enum_devices.append((UID, UID[:6])) # (UID - in hex, Device type - in hex)
        return enum_devices

    def subscribeToDevices(self, deviceList):
        """ deviceList - List of tuples of UIDs and delays. Creates a dictionary
        storing UID, delay, time created (ms), previous data, whether data is
        low and flip times (the next time the data should flip). Flip is when
        data changes low to high or high to low.

        """

        for UID, delay in deviceList:
            if UID in self.UIDs and UID not in self.subscribedTo:
                last_time = time.time()*1000
                self.subscribedTo[UID] = {'delay': delay, 'time': last_time}
                self.subscribedTo[UID]['data'] = self.__getRandomData(UID, True)
                self.subscribedTo[UID]['is_low'] = True
                self.subscribedTo[UID]['flip_time'] = self.__calculateFlipTime(UID)
            elif UID in self.UIDs and  UID in self.subscribedTo:
                self.subscribedTo[UID]['delay'] = delay
        return 0

    def getData(self, UID):
        """ Extracts all data for specific UID. Checks whether to update data,
        flip data, or return previous data, and returns correct appropriate
        data.
        """

        delay = self.subscribedTo[UID]['delay']
        last_time = self.subscribedTo[UID]['time']
        flip_time = self.subscribedTo[UID]['flip_time']
        curr_time = time.time()*1000

        should_flip = curr_time - delay >= flip_time
        should_update = curr_time - delay >= last_time

        if should_flip and should_update:
            self.subscribedTo[UID]['time'] = curr_time
            self.subscribedTo[UID]['data'] =  self.__getRandomData(UID, self.subscribedTo[UID]['is_low'])
            self.subscribedTo[UID]['flip_time'] = self.__calculateFlipTime(UID)
            self.subscribedTo[UID]['is_low'] = not self.subscribedTo[UID]['is_low']
        elif should_update:
            self.subscribedTo[UID]['time'] = curr_time
            self.subscribedTo[UID]['data'] = self.__getRandomData(UID, not self.subscribedTo[UID]['is_low'])
        return self.subscribedTo[UID]['data'] #returns sensor data

    def __calculateFlipTime(self, UID):
        """ Determines time of flip. """

        rand, last_time = random.random(), self.subscribedTo[UID]['time']
        noise = random.random()
        for i in range(len(cutoffs)):
            if rand < cutoffs[i]:
                return (time.time() + noise + i)*1000

    def __getRandomData(self, UID, is_low):
        """ Finds device_type of UID and returns corresponding flipped data."""

        device_type = UID[:6]
        low, high, noise = sensor_values[device_type]
        if is_low:
            return high + (random.random() - .5) * noise
        else:
            return low + (random.random() - .5) * noise

############
## MOTORS ##
############

    def readValue(self, UID, param):
        #param values: 0 - delay, 1 - last_time, 2 - data
        try:
            return self.subscribedTo[UID][param]
        except:
            return 1

    def writeValue(self, UID, param, value):
        if param >= len(self.subscribedTo[UID]):
            return 1
        self.subscribedTo[UID][param] = value
        return 0


#############
## TESTING ##
#############

hi = Hibike()
hi.subscribeToDevices([('0x000100FFFFFFFFFFFFFFFF', 1)])
