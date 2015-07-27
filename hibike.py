import os
import sys
import serial

sys.path.append(os.getcwd()+'/lib');
from hibike_message import *

global sensorType
global dataLength
global data
sensorType = None
dataLength = None
data = None

port = serial.Serial('/dev/tty.usbmodem1421', 57600);
subscribed = False

sendSubscriptionRequest(20, 0, port);
while(True):
    m = receiveHibikeMessage(port);
    if m is not None:
        if subscribed and m.messageId == HibikeMessageType.SubscriptionSensorUpdate:
            sensorType = m.payload['sensorTypeId']
            dataLength = m.payload['sensorReadingLength']
            data = m.payload['reading']
            print(data)
        elif m.messageId == HibikeMessageType.SubscriptionResponse and \
             m.payload == SubscriptionResponse.Success:
            print('Successfully subscribed to receive sensor readings.');
            subscribed = True;
