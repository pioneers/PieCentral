import lib.hibike_message

sensorType = None
data = None

input('Press any key to subscribe to Arduino...');
sendSubscriptionRequest(100, 0, 0);
while(True):
    m = receiveHibikeMessage(0);
    if m is not None and \
       m.messageId == HibikeMessageType.SubscriptionSensorUpdate:
        sensorType = m.payload['sensorTypeId']
        data = m.payload['reading']
