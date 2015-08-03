import struct
from enum import Enum

"""
Message IDs for each type of hibike message.
"""
class HibikeMessageType(Enum):
    SubscriptionRequest  = 0x00
    SubscriptionResponse = 0x01
    SensorUpdate         = 0x02
    Error                = 0xFF

"""
Sensor Type IDs.
"""
class SensorType(Enum):
    LimitSwitch  = 0x00
    LineFollower = 0x01

"""
More specific error codes.
"""
class ErrorCode(Enum):
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


class HibikeMessage:
    def __init__(self, messageId, controllerId, serial = None):
        assert isinstance(messageId, HibikeMessageType)
        self.__messageId = messageId
        self.__controllerId = controllerId
        self.__checksum = None
        self.__serial = serial
    def getMessageId():
        return self.__messageId
    def getControllerId():
        return self.__controllerId
    def getChecksum():
        self.__calculateChecksum()
        return self.__checksum
    # relatively ghetto way of forcing overrides of __calculateChecksum() and send()
    # without using python's builtin abstract base class which has all sorts of weirdness
    def __calculateChecksum():
        raise HibikeMessageException("Must override the HibikeMessage __calculateChecksum method.");
    def send():
        raise HibikeMessageException("Must override the HibikeMessage send method.");

class SubscriptionRequest(HibikeMessage):
    def __init__(self, controllerId, subscriptionDelay, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.SubscriptionRequest,
                               controllerId, serial)
        # assert subscriptionDelay is a uint32
        self.__subscriptionDelay = subscriptionDelay
    def getSubscriptionDelay():
        return self.__subscriptionDelay
    def __calculateChecksum():
        if self.__checksum is not None:
            return
        self.__checksum = self.__messageId.value
        self.__checksum ^= self.__controllerId
        self.__checksum ^= getByte(self.__subscriptionDelay, 0)
        self.__checksum ^= getByte(self.__subscriptionDelay, 1)
        self.__checksum ^= getByte(self.__subscriptionDelay, 2)
        self.__checksum ^= getByte(self.__subscriptionDelay, 3)
    def send():
        assert serial is not None
        self.__calculateChecksum()
        self.__serial.write(struct.pack('<B', self.__messageId.value))
        self.__serial.write(struct.pack('<B', self.__controllerId))
        self.__serial.write(struct.pack('<I', self.__subscriptionDelay))
        self.__serial.write(struct.pack('<B', self.__checksum))


class SubscriptionResponse(HibikeMessage):
    def __init__(self, controllerId, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.SubscriptionResponse,
                               controllerId, serial)
    def __calculateChecksum():
        if self.__checksum is not None:
            return
        self.__checksum = self.__messageId.value
        self.__checksum ^= self.__controllerId
    def send():
        assert serial is not None
        self.__calculateChecksum()
        self.__serial.write(struct.pack('<B', self.__messageId.value))
        self.__serial.write(struct.pack('<B', self.__controllerId))
        self.__serial.write(struct.pack('<B', self.__checksum))

class SensorUpdate(HibikeMessage):
    def __init__(self, controllerId, sensorTypeId, sensorReadingLength, data, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.SensorUpdate, controllerId, serial)
        assert isinstance(sensorTypeId, SensorType)
        # assert uint8
        self.__sensorTypeId = sensorTypeId
        # assert uint16
        self.__sensorReadingLength = sensorReadingLength
        # assert size in bytes is consistent with sensorReadingLength
        self.__data = data
    def getSensorTypeId():
        return self.__sensorTypeId
    def getSensorReadingLength():
        return self.__sensorReadingLength
    def getData():
        return self.__data
    def __calculateChecksum():
        if self.__checksum is not None:
            return
        self.__checksum = self.__messageId.value
        self.__checksum ^= self.__controllerId
        self.__checksum ^= self.__sensorTypeId.value
        self.__checksum ^= getByte(self.__sensorReadingLength, 0)
        self.__checksum ^= getByte(self.__sensorReadingLength, 1)
        for i in range(self.__sensorReadingLength):
            self.__checksum ^= getByte(self.__data, i)
    def send():
        assert serial is not None
        self.__calculateChecksum()
        self.__serial.write(struct.pack('<B', self.__messageId.value))
        self.__serial.write(struct.pack('<B', self.__controllerId))
        self.__serial.write(struct.pack('<B', self.__sensorTypeId.value))
        self.__serial.write(struct.pack('<H', self.__sensorReadingLength))
        for i in range(self.__sensorReadingLength):
            self.__serial.write(struct.pack('<B', getByte(self.__data, i)))
        self.__serial.write(struct.pack('<B', self.__checksum))

class Error(HibikeMessage):
    def __init__(self, controllerId, errorCode, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.Error, controllerId, serial)
        assert isinstance(errorCode, ErrorCode)
        self.__errorCode = errorCode
    def getErrorCode():
        return self.__errorCode
    def __calculateChecksum():
        if self.__checksum is not None:
            return
        self.__checksum = self.__messageId.value
        self.__checksum ^= self.__controllerId
        self.__checksum ^= self.__errorCode.value
    def send():
        assert serial is not None
        self.__calculateChecksum()
        self.__serial.write(struct.pack('<B', self.__messageId.value))
        self.__serial.write(struct.pack('<B', self.__controllerId))
        self.__serial.write(struct.pack('<B', self.__errorCode.value))
        self.__serial.write(struct.pack('<B', self.__checksum))

def receiveHibikeMessage(serial):
    assert serial is not None
    if serial.inWaiting() is 0:
        return None
    m = None
    messageId = HibikeMessageType(struct.unpack('<B', serial.read(1))[0])
    controllerId = struct.unpack('<B', serial.read(1))

    if messageId is HibikeMessageType.SubscriptionResponse:
        m = SubscriptionResponse(controllerId, serial)

    elif messageId is HibikeMessageType.SensorUpdate:
        sensorTypeId = SensorType(struct.unpack('<B', serial.read(1))[0])
        sensorReadingLength = struct.unpack('<H', serial.read(2))
        data = 0
        for i in range(sensorReadingLength):
            #FIXME: check on endianness
            data = data << 8 | struct.unpack('<B', serial.read(1))
        m = SensorUpdate(controllerId, sensorTypeId, sensorReadingLength, data, serial)

    elif messageId is HibikeMessageType.Error:
        errorCode = ErrorCode(struct.unpack('<B', serial.read(1))[0])
        m = Error(controllerId, errorCode, serial)

    checksum = struct.unpack('<B', serial.read(1))
    if checksum ^ m.getChecksum() is not 0:
        Error(controllerId, ErrorCode.ChecksumMismatch, serial).send()
        return None
    return m
