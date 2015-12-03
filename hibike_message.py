from __future__ import print_function
# Rewritten because Python.__version__ != 3
import serial
import struct
import pdb
# Dictionary of message types: message id
messageTypes = {
  "SubscriptionRequest" :  0x00,
  "SubscriptionResponse" : 0x01,
  "DataUpdate" :           0x02,
  "DeviceUpdate" :         0x03,
  "DeviceStatus" :         0x04,
  "DeviceResponse" :       0x05,
  "Ping" :                 0x06,
  "Error" :                0xff
}

# Dictionary of device types: enumeration
deviceTypes = {
  "Limit Switch" :         0x00,
  "Line Follower" :        0x01,
  "Potentiometer" :        0x02,
  "Encoder" :              0x03,
  "Battery Buzzer" :       0x04,
  "Team Flag" :            0x05,
  "Grizzly" :              0x06,
  "Servo Control" :        0x07,
  "Linear Actuator" :      0x08
}


# Dictionary of message types: payload length
messagePayloadLengths = {
  messageTypes["SubscriptionRequest"] :  2,
  messageTypes["SubscriptionResponse"] : 13,
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
    self._length = len(payload)

  def getmessageID(self):
    return self._messageID

  # Returns a copy of payload as a bytearray
  def getPayload(self):
    return self._payload[:]

  def toByte(self):
    m_buff = bytearray()
    m_buff.append(self._messageID)
    m_buff.append(self._length)
    m_buff.extend(self.getPayload())
    return m_buff

  def __str__(self):
    return str([self._messageID] + [self._length] + list(self._payload))

  def __repr__(self):
    return str(self)




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
def checksum(data):
  # Remove this later after development
  assert type(data) == bytearray, "data must be a bytearray"

  chk = data[0]
  for i in range(1, len(data)):
    chk ^= data[i]
  return chk

# Sends this message
# Computes the checksum
# Then sends each byte of the message, and finally sends the checksum byte
def send(serial_conn, message):
  m_buff = message.toByte()
  chk = checksum(m_buff)
  m_buff.append(chr(chk))
  encoded = cobs_encode(m_buff)
  out_buf = bytearray([0x00, len(encoded)]) + encoded
  serial_conn.write(out_buf)


def make_sub_request(delay):
  """ Makes and returns SubscriptionRequest message."""
  temp_payload = struct.pack('<H', delay)
  payload = bytearray(temp_payload)
  message = HibikeMessage(messageTypes["SubscriptionRequest"], payload)
  return message

def make_device_update(param, value):
  """ Makes and returns DeviceUpdate message."""
  temp_payload = struct.pack('<BI', param, value)
  payload = bytearray(temp_payload)
  message = HibikeMessage(messageTypes["DeviceUpdate"], payload)
  return message

def make_device_status(param):
  """ Makes and returns DeviceStatus message."""
  temp_payload = struct.pack('<B', param)
  payload = bytearray(temp_payload)
  message = HibikeMessage(messageTypes["DeviceStatus"], payload)
  return message

def make_error(error_code):
  """ Makes and returns Error message."""
  temp_payload = struct.pack('<B', error_code)
  payload = bytearray(temp_payload)
  message = HibikeMessage(messageTypes["Error"], payload)
  return message

def make_ping():
  """ Makes and returns Ping message."""
  payload = bytearray()
  message = HibikeMessage(messageTypes["Ping"], payload)
  return message


# constructs a new object Message by continually reading from input
# Uses dictionary to figure out length of data to know how many bytes to read
# Returns:
    # None if no message
    # -1 if checksum does not match
    # Otherwise returns a new HibikeMessage with message contents
def read(serial_conn):
  
  # deal with cobs encoding
  while serial_conn.inWaiting() > 0:
    if struct.unpack('<B', serial_conn.read())[0] == 0:
      break
  else:
    return None
  message_size = struct.unpack('<B', serial_conn.read())[0]
  encoded_message = serial_conn.read(message_size)
  message = cobs_decode(encoded_message)
  

  if len(message) < 2:
    return None
  messageID, payloadLength = struct.unpack('<BB', message[:2])
  if len(message) < 2 + payloadLength + 1:
    return None
  payload = message[2:2 + payloadLength]

  chk = struct.unpack('<B', message[2+payloadLength:2+payloadLength+1])[0]
  if chk != checksum(message[:-1]):
    print(chk, checksum(message[:-1]), list(message))
    return -1

  return HibikeMessage(messageID, payload)

# cobs helper functions
def cobs_encode(data):
  output = bytearray()
  curr_block = bytearray()
  for byte in data:
    if byte:
      curr_block.append(byte)
      if len(curr_block) == 254:
        output.append(1 + len(curr_block))
        output.extend(curr_block)
        curr_block = bytearray()
    else:
      output.append(1 + len(curr_block))
      output.extend(curr_block)
      curr_block = bytearray()
  output.append(1 + len(curr_block))
  output.extend(curr_block)
  return output

def cobs_decode(data):
  output = bytearray()
  index = 0
  while (index < len(data)):
    block_size = ord(data[index]) - 1
    index += 1
    if index + block_size > len(data):
      return bytearray()
    output.extend(data[index:index + block_size])
    index += block_size
    if block_size + 1 < 255 and index < len(data):
      output.append(0)
  return output
