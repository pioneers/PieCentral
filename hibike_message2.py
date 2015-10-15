# Rewritten because Python.__version__ != 3
import serial

# note that this has to be hard coded until enumeration works
serial = serial.Serial('/dev/ttyUSB0', 115200)

# Dictionary of message types: message id
messageTypes = {
  "SubscriptionRequest" : 0x00,
  "SubscriptionResponse" : 0x01,
}

# Dictionary of message types: payload length
messagePayloadLengths = {
  messageTypes["SubscriptionRequest"] : 1,
  messageTypes["SubscriptionResponse"] : 1,
}

class HibikeMessage:
    def __init__(self, messageId, controllerId, payload):
        assert messageId in messageTypes.values()
        self._messageId = messageId
        self._controllerId = controllerId
        self._payload = payload[:]

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

    # Returns a copy of payload as a bytearray
    def getPayload(self):
      return self._payload[:]

    def serialize(self):
      message = bytearray()
      message.append(_messageId)
      message.append(_controllerId)
      for b in self._payload:
        message.append(b)
      return message


# Given a message, computes the checksum
def checksum(message):
  chk = message[0]
  for i in range(2, len(message), 2):
    chk ^= message[i]
  return chk

# Sends this message
# Computes the checksum
# Then sends each byte of the message, and finally sends the checksum byte
def send(message):
  chk = checksum(message)
  serial.write(message)
  serial.write(chr(chk))

# constructs a new object Message by continually reading from input
# Uses dictionary to figure out length of data to know how many bytes to read
# Returns: 
    # None if no message
    # -1 if checksum does not match
    # Otherwise returns a new HibikeMessage with message contents
def read():
  if serial.inWaiting() == 0:
    return None

  message = bytearray(serial.read(2))
  messageId, controllerId = message[0], message[1]
  payloadLength = messagePayloadLengths[messageId]
  payload = bytearrayserial.read(payloadLength)
  message += payload
  chk = serial.read()
  if chk != checksum(message):
    return -1

  return HibikeMessage(messageId, controllerId, payload)
