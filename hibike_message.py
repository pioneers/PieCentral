import struct
from enum import Enum

"""
Message IDs for each type of hibike message.
"""
class HibikeMessageType(Enum):
    SubscriptionRequest  = 0x00
    SubscriptionResponse = 0x01
    DataUpdate           = 0x02
    DeviceUpdate         = 0x03
    DeviceStatus         = 0x04
    DeviceResponse       = 0x05
    Error                = 0xFF

"""
Device Type IDs.
"""
class DeviceType(Enum):
    LimitSwitch    = 0x00
    LineFollower   = 0x01
    Potentiometer  = 0x02
    Encoder        = 0x03
    BatteryBuzzer  = 0x04
    TeamFlag       = 0x05
    Grizzly        = 0x06
    Servo          = 0x07
    LinearActuator = 0x08

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

    # return the top 16 bits of controllerID
    def getDeviceType(self):
        return int(self.getControllerId() >> 72)

    # return bits [71: 64]
    def getYear(self):
        temp = self.getControllerId() >> 64
        return int(temp & 0xff)

    # return bits[63: 0]
    def getID(self):
        return self.getControllerId() & 0xffffffffffffffff

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

class DataUpdate(HibikeMessage):
    def __init__(self, controllerId, DeviceTypeId, deviceReadingLength, data, serial = None):
        HibikeMessage.__init__(self, HibikeMessageType.DataUpdate, controllerId, serial)
        assert isinstance(DeviceTypeId, DeviceType)
        # assert uint8
        self._DeviceTypeId = DeviceTypeId
        # assert uint16
        self._deviceReadingLength = deviceReadingLength
        # assert size in bytes is consistent with deviceReadingLength
        self._data = data
    def getDeviceTypeId(self):
        return self._DeviceTypeId
    def getdeviceReadingLength(self):
        return self._deviceReadingLength
    def getData(self):
        return self._data
    def _calculateChecksum(self):
        if self._checksum is not None:
            return
        self._checksum = self._messageId.value
        self._checksum ^= self._controllerId
        self._checksum ^= self._DeviceTypeId.value
        self._checksum ^= getByte(self._deviceReadingLength, 0)
        self._checksum ^= getByte(self._deviceReadingLength, 1)
        for i in range(self._deviceReadingLength):
            self._checksum ^= getByte(self._data, i)
    def send(self):
        assert self._serial is not None
        self._calculateChecksum()
        self._serial.write(struct.pack('<B', self._messageId.value))
        self._serial.write(struct.pack('<B', self._controllerId))
        self._serial.write(struct.pack('<B', self._DeviceTypeId.value))
        self._serial.write(struct.pack('<H', self._deviceReadingLength))
        for i in range(self._deviceReadingLength):
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

    elif messageId is HibikeMessageType.DataUpdate:
        DeviceTypeId = DeviceType(struct.unpack('<B', serial.read(1))[0])
        deviceReadingLength = struct.unpack('<H', serial.read(2))[0]
        # FIXME: this is currently hardcoded to only work with reading lengths
        # FIXME: that are four bytes long. Changing this to be more general
        # FIXME: should be more or less the code in the docstring below, but
        # FIXME: the endianness is a little bit tricky
        data = struct.unpack('<I', serial.read(4))[0]
        """
        data = 0
        for i in range(deviceReadingLength):
            data = data << 8 | struct.unpack('<B', serial.read(1))[0]
        """
        m = DataUpdate(controllerId, DeviceTypeId, deviceReadingLength, data, serial)

    elif messageId is HibikeMessageType.Error:
        errorCode = ErrorCode(struct.unpack('<B', serial.read(1))[0])
        m = Error(controllerId, errorCode, serial)

    checksum = struct.unpack('<B', serial.read(1))[0]
    if checksum ^ m.getChecksum() is not 0:
        Error(controllerId, ErrorCode.ChecksumMismatch, serial).send()
        return None
    return m
