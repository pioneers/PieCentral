import os, sys
sys.path.append(os.getcwd()+'/lib');
import hibike_message as HibikeMessage

sensorType = None
data = None

raw_input('Press any key to subscribe to Arduino...');
HibikeMessage.sendSubscriptionRequest(100, 0, 0);
while(True):
    m = HibikeMessage.receiveHibikeMessage(0);
    if m is not None and \
       m.messageId == HibikeMessageType.SubscriptionSensorUpdate:
        sensorType = m.payload['sensorTypeId']
        data = m.payload['reading']
