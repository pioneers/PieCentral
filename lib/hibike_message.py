import struct
from enum import Enum

"""
Message IDs for each type of hibike message.
"""
class HibikeMessageType(Enum):
    SubscriptionRequest      = 0x00
    SubscriptionResponse     = 0x01
    SubscriptionSensorUpdate = 0x02
    SensorUpdateRequest      = 0x03
    SensorUpdate             = 0x04
    Error                    = 0xFF

"""
SubscriptionResponse status codes.
"""
class SubscriptionResponse(Enum):
    Success      = 0x00
    GenericError = 0xFF

"""
Sensor Type IDs.
"""
class SensorType(Enum):
    LimitSwitch  = 0x00
    LineFollower = 0x01

"""
More specific error codes.
"""
class Error(Enum):
    InvalidMessageType = 0xFB
    MalformedMessage   = 0xFC
    InvalidArduinoId   = 0xFD
    ChecksumMismatch   = 0xFE
    GenericError       = 0xFF

class HibikeMessageException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getByte(value, index):
    return (value >> (index*8)) & 0xFF

"""
A Hibike message.
Each hibike message, aside from the properties defined in the spec
(found in ../README.md), each HibikeMessage also keeps track of the
port it should be sent over, allowing it to essentially sent itself
using HibikeMessage.send().
"""
class HibikeMessage:
    # an integer containing the message_id of this message
    # see the HibikeMessageType enum.
    messageId = None

    # an integer containing either the controller_id this message
    # is being sent to (for an outgoing message), or the controller_id
    # of the controller this message is coming from (for an incoming message)
    controllerId = None

    # either an integer or dictionary containing the data for this message
    payload = None

    # an 8 bit integer calculated either right before sending a message or
    # immediately upon receiving one.
    checksum = None

    def __init__(self, messageId, controllerId, payload):
        self.messageId = messageId
        self.controllerId = controllerId
        self.payload = payload
        self.__verifyMessage()

    """
    Ensures that the message constructed appears to be sane.
    """
    def __verifyMessage(self):
        assert isinstance(self.messageId, HibikeMessageType)
        # TODO: add more checks/asserts to ensure that the values of
        #       payload are within possible ranges.
        if self.messageId is HibikeMessageType.SubscriptionRequest:
            assert type(self.payload) is int
            # verify that self.payload can fit in a 32 bit uint
        elif self.messageId is HibikeMessageType.SubscriptionResponse:
            assert isinstance(self.payload, SubscriptionResponse)
        elif self.messageId is HibikeMessageType.SubscriptionSensorUpdate:
            assert type(self.payload) is dict
            # verify that self.payload contains sensorTypeId, sensorReadingLength,
            # and data and that each field is sensible.
        elif self.messageId is HibikeMessageType.Error:
            assert isinstance(self.payload, Error)
        else:
            raise HibikeMessageException('Message type currently unsupported.')

    def calculateChecksum(self):
        checksum = 0
        checksum ^= self.messageId.value
        checksum ^= self.controllerId
        if self.messageId == HibikeMessageType.SubscriptionRequest:
            checksum ^= (self.payload & 0xFF) ^ (self.payload>>8 & 0xFF) ^ \
                        (self.payload >>16 & 0xFF) ^ (self.payload >>24 & 0xFF)
        elif self.messageId == HibikeMessageType.SensorUpdateRequest:
            pass
        elif self.messageId == HibikeMessageType.SubscriptionResponse or \
             self.messageId == HibikeMessageType.Error:
            checksum ^= self.payload.value & 0xFF
        elif self.messageId == HibikeMessageType.SubscriptionSensorUpdate:
            checksum ^= self.payload['sensorTypeId'].value & 0xFF
            checksum ^= self.payload['sensorReadingLength'] & 0xFF
            checksum ^= (self.payload['sensorReadingLength'] >> 8) & 0xFF
            length = self.payload['sensorReadingLength']
            data = self.payload['reading']
            for i in range(length):
                checksum ^= getByte(data, i)
        else:
            raise HibikeMessageExeption
        return checksum

"""
Send HibikeMessage m over port
"""
def sendHibikeMessage(m, port):
    # TODO: fix to be able to send every message type.
    #       it's also definitely better to send the entire message
    #       at once as opposed to marshalling and sending off
    #       small parts
    m.checksum = m.calculateChecksum()
    port.write(struct.pack('<B', m.messageId.value))
    port.write(struct.pack('<B', m.controllerId))
    if m.messageId == HibikeMessageType.SubscriptionRequest:
        port.write(struct.pack('<I', m.payload))
    else:
        port.write(struct.pack('<B', m.payload.value))
    port.write(struct.pack('<B', m.checksum))

"""
Receives a Hibike Message from the given serial port.
Returns None if no data is available on the serial port.
"""
def receiveHibikeMessage(port):
    if port.inWaiting() == 0:
        return None
    payload = None
    messageId = HibikeMessageType(struct.unpack('<B', port.read(1))[0])
    controllerId = struct.unpack('<B', port.read(1))[0]
    if messageId == HibikeMessageType.SubscriptionResponse:
        payload = SubscriptionResponse(struct.unpack('<B', port.read(1))[0])
    elif messageId == HibikeMessageType.Error:
        payload = Error(struct.unpack('<B', port.read(1))[0])
    elif messageId == HibikeMessageType.SubscriptionSensorUpdate or \
         messageId == HibikeMessageType.SensorUpdate:
        payload = {}
        payload['sensorTypeId'] = SensorType(struct.unpack('<B', port.read(1))[0])
        payload['sensorReadingLength'] = struct.unpack('<H', port.read(2))[0]
        # figure out what to do with the still serialized data later
        # currently kludged so that limit switch stuff works
        # TODO: smarter unpacking that works for sensors of any type
        payload['reading'] = struct.unpack('<B', port.read(payload['sensorReadingLength']))[0]
    checksum = struct.unpack('<B', port.read(1))[0]
    message = HibikeMessage(messageId, controllerId, payload, port)
    if message.calculateChecksum() != checksum:
        errorMessage = HibikeMessage(HibikeMessageType.Error, controllerId, Error.ChecksumMismatch, port)
        errorMessage.sendMessage()
        raise HibikeMessageExeption("incorrect checksum")
    return message

"""
Sends a subscriptionSensorRequest that requests new sensor
data every delay ms to controllerId over port.
"""
def sendSubscriptionRequest(delay, controllerId, port):
    message = HibikeMessage(HibikeMessageType.SubscriptionRequest,
                            controllerId, delay, port)
    sendHibikeMessage(message, port);

