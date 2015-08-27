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
        self._messageId = messageId
        self._controllerId = controllerId
        self._checksum = None
        self._serial = serial
    def getMessageId(self):
        return self._messageId
    def getControllerId(self):
        return self._controllerId
    def getChecksum(self):
        self._calculateChecksum()
        return self._checksum
    # relatively ghetto way of forcing overrides of _calculateChecksum() and send()
    # without using python's builtin abstract base class which has all sorts of weirdness
    def _calculateChecksum(self):
        raise HibikeMessageException("Must override the HibikeMessage _calculateChecksum method.");
    def send(self):
        raise HibikeMessageException("Must override the HibikeMessage send method.");

class SubscriptionRequest(HibikeMessage):
    def __init__(self, controllerId, subscriptionDelay, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.SubscriptionRequest, controllerId, serial)
        # assert subscriptionDelay is a uint32
        self._subscriptionDelay = subscriptionDelay
    def getSubscriptionDelay(self):
        return self._subscriptionDelay
    def _calculateChecksum(self):
        if self._checksum is not None:
            return
        self._checksum = self._messageId.value
        self._checksum ^= self._controllerId
        self._checksum ^= getByte(self._subscriptionDelay, 0)
        self._checksum ^= getByte(self._subscriptionDelay, 1)
        self._checksum ^= getByte(self._subscriptionDelay, 2)
        self._checksum ^= getByte(self._subscriptionDelay, 3)
    def send(self):
        assert self._serial is not None
        self._calculateChecksum()
        self._serial.write(struct.pack('<B', self._messageId.value))
        self._serial.write(struct.pack('<B', self._controllerId))
        self._serial.write(struct.pack('<I', self._subscriptionDelay))
        self._serial.write(struct.pack('<B', self._checksum))


class SubscriptionResponse(HibikeMessage):
    def __init__(self, controllerId, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.SubscriptionResponse, controllerId, serial)
    def _calculateChecksum(self):
        if self._checksum is not None:
            return
        self._checksum = self._messageId.value
        self._checksum ^= self._controllerId
    def send(self):
        assert self._serial is not None
        self._calculateChecksum()
        self._serial.write(struct.pack('<B', self._messageId.value))
        self._serial.write(struct.pack('<B', self._controllerId))
        self._serial.write(struct.pack('<B', self._checksum))

class SensorUpdate(HibikeMessage):
    def __init__(self, controllerId, sensorTypeId, sensorReadingLength, data, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.SensorUpdate, controllerId, serial)
        assert isinstance(sensorTypeId, SensorType)
        # assert uint8
        self._sensorTypeId = sensorTypeId
        # assert uint16
        self._sensorReadingLength = sensorReadingLength
        # assert size in bytes is consistent with sensorReadingLength
        self._data = data
    def getSensorTypeId(self):
        return self._sensorTypeId
    def getSensorReadingLength(self):
        return self._sensorReadingLength
    def getData(self):
        return self._data
    def _calculateChecksum(self):
        if self._checksum is not None:
            return
        self._checksum = self._messageId.value
        self._checksum ^= self._controllerId
        self._checksum ^= self._sensorTypeId.value
        self._checksum ^= getByte(self._sensorReadingLength, 0)
        self._checksum ^= getByte(self._sensorReadingLength, 1)
        for i in range(self._sensorReadingLength):
            self._checksum ^= getByte(self._data, i)
    def send(self):
        assert self._serial is not None
        self._calculateChecksum()
        self._serial.write(struct.pack('<B', self._messageId.value))
        self._serial.write(struct.pack('<B', self._controllerId))
        self._serial.write(struct.pack('<B', self._sensorTypeId.value))
        self._serial.write(struct.pack('<H', self._sensorReadingLength))
        for i in range(self._sensorReadingLength):
            self._serial.write(struct.pack('<B', getByte(self._data, i)))
        self._serial.write(struct.pack('<B', self._checksum))

class Error(HibikeMessage):
    def __init__(self, controllerId, errorCode, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.Error, controllerId, serial)
        assert isinstance(errorCode, ErrorCode)
        self._errorCode = errorCode
    def getErrorCode(self):
        return self._errorCode
    def _calculateChecksum(self):
        if self._checksum is not None:
            return
        self._checksum = self._messageId.value
        self._checksum ^= self._controllerId
        self._checksum ^= self._errorCode.value
    def send(self):
        assert self._serial is not None
        self._calculateChecksum()
        self._serial.write(struct.pack('<B', self._messageId.value))
        self._serial.write(struct.pack('<B', self._controllerId))
        self._serial.write(struct.pack('<B', self._errorCode.value))
        self._serial.write(struct.pack('<B', self._checksum))

def receiveHibikeMessage(serial):
    assert serial is not None
    if serial.inWaiting() is 0:
        return None
    m = None
    messageId = HibikeMessageType(struct.unpack('<B', serial.read(1))[0])
    controllerId = struct.unpack('<B', serial.read(1))[0]

    if messageId is HibikeMessageType.SubscriptionResponse:
        m = SubscriptionResponse(controllerId, serial)

    elif messageId is HibikeMessageType.SensorUpdate:
        sensorTypeId = SensorType(struct.unpack('<B', serial.read(1))[0])
        sensorReadingLength = struct.unpack('<H', serial.read(2))[0]
        # FIXME: this is currently hardcoded to only work with reading lengths
        # FIXME: that are four bytes long. Changing this to be more general
        # FIXME: should be more or less the code in the docstring below, but
        # FIXME: the endianness is a little bit tricky
        data = struct.unpack('<I', serial.read(4))[0]
        """
        data = 0
        for i in range(sensorReadingLength):
            data = data << 8 | struct.unpack('<B', serial.read(1))[0]
        """
        m = SensorUpdate(controllerId, sensorTypeId, sensorReadingLength, data, serial)

    elif messageId is HibikeMessageType.Error:
        errorCode = ErrorCode(struct.unpack('<B', serial.read(1))[0])
        m = Error(controllerId, errorCode, serial)

    checksum = struct.unpack('<B', serial.read(1))[0]
    if checksum ^ m.getChecksum() is not 0:
        Error(controllerId, ErrorCode.ChecksumMismatch, serial).send()
        return None
    return m
