import os
import sys
import serial
import time

sys.path.append(os.getcwd()+'/../lib');
from hibike_message import *

global sensorType
global dataLength
global data
sensorType = None
dataLength = None
data = None

# note that this has to be hard coded until enumeration works
serial = serial.Serial('/dev/tty.usbmodem1411', 115200)
lastTime = None

raw_input('press enter to subscribe to sensor data...')

while True:
    print('sending subscription request...')
    SubscriptionRequest(0, 10, serial).send()
    time.sleep(.015);
    m = receiveHibikeMessage(serial)
    if m is not None and m.getMessageId() is HibikeMessageType.SubscriptionResponse:
        print('Successfully subscribed to receive sensor readings.')
        lastTime = time.time()
        break
    elif m is not None: #TODO: write proper error handling
        print(m.getMessageId())

while True:
    m = receiveHibikeMessage(serial);
    if m is not None:
        if m.getMessageId() is HibikeMessageType.SubscriptionSensorUpdate:
            sensorType = m.getSensorTypeId()
            dataLength = m.getSensorReadingLength()
            data = m.getData()
            curTime = time.time()
            print('sensor reading: ' + str(data))
            print('time elapsed in ms since last reading: '+str(1000*(curTime-lastTime)))
            lastTime = curTime
        #TODO: more proper error handling
