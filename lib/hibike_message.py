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
    Success = 0
    GenericError = 0xFF

"""
Sensor Type IDs.
"""
class SensorType(Enum):
    LimitSwitch = 0
    LineFollower = 1

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
        # TODO: add more checks/asserts to ensure that the values of
        #       payload are within possible ranges.
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
        checksum ^= self.messageId.value
        checksum ^= self.controllerId
        if self.messageId == HibikeMessage.SubscriptionRequest:
            checksum ^= (self.payload & 0xFF) ^ (self.payload>>8 & 0xFF) ^ \
                        (self.payload >>16 & 0xFF) ^ (self.payload >>24 & 0xFF)
        elif self.messageId == HibikeMessage.SensorUpdateRequest:
            pass
        elif self.messageId == HibikeMessage.SubscriptionResponse or \
             self.messageId == HibikeMessage.Error:
            checksum ^= self.payload & 0xFF
        elif self.messageId == HibikeMessage.SubscriptionSensorUpdate:
            checksum ^= payload['sensorTypeId']
            checksum ^= payload['sensorReadingLength'] & 0xFF
            checksum ^= (payload['sensorReadingLength'] >> 8) & 0xFF
            length = payload['sensorReadingLength']
            data = payload['reading']
            for i in range(length):
                checksum ^= __getByte(data, i)
        else:
            raise HibikeMessageExeption
        return checksum

    def __getByte(value, index):
        return (value >> (index*8)) & 0xFF

    # kludged for now to only be able to send SubscriptionRequests
    def sendMessage(self):
        self.checksum = self.__calculateChecksum()
        ser = serial.Serial()
        ser.port = self.__port
        ser.baudrate = 57600
        ser.open()
        message = struct.pack('<BBIB', self.messageId, self.controllerId,
                              self.payload, self.checksum)
        ser.write(message)
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
    ser.open()
    payload = 0
    if ser.inWaiting() == 0:
        return None
    messageId = HibikeMessageType(struct.unpack('<B', ser.read(1)))
    controllerId = struct.unpack('<B', ser.read(1))
    if messageId == HibikeMessageType.SubscriptionResponse.value or \
       messageId == HibikeMessageType.Error.value:
        payload = struct.unpack('<B', ser.read(1))
    elif messageId == HibikeMessageType.SubscriptionSensorUpdate.value or \
         messageId == HibikeMessageType.SensorUpdate.value:
        payload = {}
        payload['sensorTypeID'] = struct.unpack('<B', ser.read(1))
        payload['sensorReadingLength'] = struct.unpack('<B', ser.read(2))
        # figure out what to do with the still serialized data later
        payload['reading'] = ser.read(payload['sensorReadingLength'])
    checksum = struct.unpack('<B', ser.read(1))
    message = HibikeMessage(messageId, controllerId, payload, port)
    if message.__calculateChecksum() != message.checksum:
        errorMessage = HibikeMessage(HibikeMessageType.Error, controllerId, Error.ChecksumMismatch, port)
        errorMessage.sendMessage()
        raise HibikeMessageExeption("incorrect checksum")
    return message
