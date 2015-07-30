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

port = serial.Serial('/dev/tty.usbmodem1411', 57600)
last_time = time.time()


raw_input('press enter to subscribe to sensor data...')

while True:
    print('sending subscription request...')
    sendSubscriptionRequest(10, 0, port)
    time.sleep(.015);
    m = receiveHibikeMessage(port)
    if m is not None and \
       m.messageId == HibikeMessageType.SubscriptionResponse and \
       m.payload == SubscriptionResponse.Success:
        print('Successfully subscribed to receive sensor readings.')
        break
    elif m is not None: #TODO: proper error handling
        print(m.messageId)
        print(m.payload)

while True:
    m = receiveHibikeMessage(port);
    if m is not None:
        if m.messageId == HibikeMessageType.SubscriptionSensorUpdate:
            sensorType = m.payload['sensorTypeId']
            dataLength = m.payload['sensorReadingLength']
            data = m.payload['reading']

            cur_time = time.time()
            print('sensor reading: ' + str(data))
            print('time elapsed in ms since last reading: ' + str(1000*(cur_time - last_time)))
            last_time = cur_time
        #TODO: more proper error handling
