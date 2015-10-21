# Rewritten because Python.__version__ != 3
import serial

# note that this has to be hard coded until enumeration works
serial = serial.Serial('/dev/ttyUSB0', 115200)

# Dictionary of message types: message id
messageTypes = {
  "SubscriptionRequest" :  0x00,
  "SubscriptionResponse" : 0x01,
  "DataUpdate" :           0x02,
  "DeviceStatus" :         0x03,
  "DeviceUpdate" :         0x04,
  "DeviceResponse" :       0x05,
  "Error" :                0xff
}

# Dictionary of message types: payload length
messagePayloadLengths = {
  messageTypes["SubscriptionRequest"] :  1,
  messageTypes["SubscriptionResponse"] : 12,
  # TODO: find a clean way to not hardcode this
  messageTypes["DataUpdate"] :           1,
  messageTypes["DeviceUpdate"] :         5,
  messageTypes["DeviceStatus"] :         5,
  messageTypes["DeviceResponse"] :       5,
  messageTypes["Error"] :                1
}

# Dictionary of error names : error codes
errorCodes = {
  "InvalidMessageType" : 0xfb,
  "MalformedMessage" :   0xfc,
  "InvalidUID" :         0xfd,
  "CheckumError" :       0xfe,
  "GenericError" :       0xff
}

class HibikeMessage:
    def __init__(self, messageID, payload):
        assert messageID in messageTypes.values()
        self._messageID = messageID
        self._payload = payload[:]

    def getmessageID(self):
        return self._messageID

    # Returns a copy of payload as a bytearray
    def getPayload(self):
      return self._payload[:]

    def serialize(self):
      message = bytearray()
      message.append(_messageID)
      for b in self._payload:
        message.append(b)
      return message


# return the top 16 bits of UID
def getDeviceType(uid):
    return int(uid >> 72)

# return bits [71: 64] of the UID
def getYear(uid):
    temp = uid >> 64
    return int(temp & 0xff)

# return bits[63: 0] of the UID
def getID(uid):
    return uid & 0xffffffffffffffff


# Given a message, computes the checksum
def checksum(message):
  # Remove this later after development
  assert type(message) == bytearray, "message must be a bytearray"

  chk = message[0]
  for i in range(2, len(message), 2):
    chk ^= message[i]
  return chk

# Sends this message
# Computes the checksum
# Then sends each byte of the message, and finally sends the checksum byte
def send(message):
  # Remove this later after development
  assert type(message) == bytearray, "message must be a bytearray"

  chk = checksum(message)
  serial.write(message)
  serial.write(chr(chk))

# constructs a new object Message by continually reading from input
# Uses dictionary to figure out length of data to know how many bytes to read
# Returns: 
    # None if no message
    # -1 if checksum does not match
    # Otherwise returns a new HibikeMessage with message contents
def read(port):
  if port.inWaiting() == 0:
    return None
  message = bytearray()

  messageID = port.read()
  message.append(messageID)

  payloadLength = messagePayloadLengths[messageID]
  payload = port.read(payloadLength)
  message.append(payload)

  chk = port.read()
  if chk != checksum(message):
    return -1

  return HibikeMessage(messageID, payload)
