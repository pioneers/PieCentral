import serial
import struct
from enum import Enum

"""
Message IDs for each type of hibike message.
"""
class HibikeMessageType(Enum):
    SubscriptionRequest = 0
    SubscriptionResponse = 1
    SubscriptionSensorUpdate = 2
    SensorUpdateRequest = 3
    SensorUpdate = 4
    Error = 0xFF

"""
SubscriptionResponse status codes.
"""
class SubscriptionResponse(Enum):
    GenericError = 0xFF

"""
Sensor Type IDs.
"""
class SensorType(Enum):
    PLACEHOLDER = 0

"""
More specific error codes.
"""
class Error(Enum):
    InvalidMessageType = 0xFB
    MalformedMessage = 0xFC
    InvalidArduinoId = 0xFD
    ChecksumMismatch = 0xFE
    GenericError = 0xFF

class HibikeMessageException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

"""
A Hibike message.
Each hibike message, aside from the properties defined in the spec
(found in ../README.md), each HibikeMessage also keeps track of the
port it should be sent over, allowing it to essentially sent itself
using HibikeMessage.send().
"""
class HibikeMessage:
    # the serial port this message should be sent over.
    __port 

    # an integer containing the message_id of this message
    # see the HibikeMessageType enum.
    messageId

    # an integer containing either the controller_id this message
    # is being sent to (for an outgoing message), or the controller_id
    # of the controller this message is coming from (for an incoming message)
    controllerId

    # either an integer or dictionary containing the data for this message
    payload

    # an 8 bit integer calculated either right before sending a message or
    # immediately upon receiving one.
    checksum

    def __init__(self, messageId, controllerId, payload, port):
        self.messageId = messageId
        self.controllerId = controllerId
        self.payload = payload
        self.__verifyMessage()
        self.__port = port

    """
    Ensures that the message constructed appears to be sane.
    """
    def __verifyMessage(self):
        assert isinstance(self.messageId, HibikeMessageType)

        #
        # TODO(vincent): add more checks/asserts to ensure that the values of
        #                payload are within possible ranges.
        #
        if self.messageId is HibikeMessageType.SubscriptionRequest:
            assert type(self.payload) is int
            # verify that self.payload can fit in a 32 bit uint
        elif self.messageId is HibikeMessageType.SubscriptionResponse:
            assert isinstance(payload, SubscriptionResponse)
        elif self.messageId is HibikeMessageType.SubscriptionSensorUpdate:
            assert type(self.payload) is dict
            # verify that self.payload contains sensorTypeId, sensorReadingLength,
            # and data and that each field is sensible.
        elif self.messageId is HibikeMessageType.Error:
            assert isinstance(payload, Error)
        else:
            raise HibikeMessageException('Message type currently unsupported.')

    def __calculateChecksum(self):
        checksum = 0
        checksum ^= self.messageId
        checksum ^= self.controllerId
        if self.messageId == HibikeMessage.SubscriptionRequest:
            checksum ^= self.payload & 0xFF
        elif self.messageId == HibikeMessage.SensorUpdateRequest:
            pass
        else:
            raise HibikeMessageExeption
        self.checksum = checksum

    def sendMessage(self):
        self.__calculateChecksum()
        ser = serial.Serial()
        ser.port = self.__port
        ser.open()
        ser.write(messageId)
        ser.write(controllerId)
        ser.write(payload)
        ser.write(checksum)
        ser.close()


"""
Sends a subscriptionSensorRequest that requests new sensor
data every delay ms to controllerId over port.
"""
def sendSubscriptionRequest(delay, controllerId, port):
    message = HibikeMessage(HibikeMessage.SubscriptionRequest,
                            controllerId, delay, port)
    message.sendMessage()

"""
Receives a Hibike Message from the given serial port.
Returns None if no data is available on the serial port.
"""
def receiveHibikeMessage(port):
    ser = serial.Serial()
    ser.port = port
    ser.open
    payload = 0
    if ser.inWaiting() == 0:
        return None
    messageId = ser.read(1)
    controllerId = ser.read(1)
    if messageId == 1:
        payload = ser.read(1)
    elif messageId == 2 or messageId == 4:
        payload = {}
        payload[sensorTypeID] = ser.read(1)
        payload[sensorReadingLength] = ser.read(2)
        payload[reading] = ser.read(payload[sensorReadingLength])
    checksum = ser.read(1)
    return HibikeMessage(messageId, controllerId, payload, checksum)
