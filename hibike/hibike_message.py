"""
Functions and classes for dealing with Hibike packets.
"""
from __future__ import print_function
# Rewritten because Python.__version__ != 3
import struct
import os
import json

CONFIG_FILE = open(os.path.join(
    os.path.dirname(__file__), 'hibikeDevices.json'), 'r')
DEVICES = json.load(CONFIG_FILE)

PARAM_MAP = {device["id"]: {param["name"]: (param["number"],
                                            param["type"],
                                            param["read"],
                                            param["write"]) for param in device["params"]}
             for device in DEVICES}
DEVICES = {device["id"]: device for device in DEVICES}
"""
structure of devices
{0:
    {"id": 0, "name": "LimitSwitch",
    "params": [
        {"number": 0, "name": "switch0", "type": "bool", "read": True, "write": False}
    ]
    }
}

"""

# Dictionary mapping param types to python struct format characters
PARAM_TYPES = {
    "bool": "?",
    "uint8_t": "B",
    "int8_t": "b",
    "uint16_t": "H",
    "int16_t": "h",
    "uint32_t": "I",
    "int32_t": "i",
    "uint64_t": "Q",
    "int64_t": "q",
    "float": "f",
    "double": "d"
}

# Dictionary of message types: message id
MESSAGE_TYPES = {
    "Ping":                 0x10,
    "SubscriptionRequest":  0x11,
    "SubscriptionResponse": 0x12,
    "DeviceRead":           0x13,
    "DeviceWrite":          0x14,
    "DeviceData":           0x15,
    "Disable":               0x16,
    "HeartBeatRequest":     0x17,
    "HeartBeatResponse":    0x18,
    "Error":                0xFF
}

# Dictionary of error names : error codes
ERROR_CODES = {
    "UnexpectedDelimiter": 0xFD,
    "CheckumError": 0xFE,
    "GenericError": 0xFF
}


class HibikeMessage:
    """
    An Hibike packet.
    """
    def __init__(self, message_id, payload):
        assert message_id in MESSAGE_TYPES.values()
        self._message_id = message_id
        self._payload = payload[:]
        self._length = len(payload)

    def get_message_id(self):
        """
        Get the message ID.
        """
        return self._message_id

    def get_payload(self):
        """
        Get a copy of the payload as a bytearray.
        """
        return self._payload[:]

    def to_bytes(self):
        """
        A representation of this message in bytes.
        """
        m_buff = bytearray()
        m_buff.append(self._message_id)
        m_buff.append(self._length)
        m_buff.extend(self.get_payload())
        return m_buff

    def __str__(self):
        return str([self._message_id] + [self._length] + list(self._payload))

    def __repr__(self):
        return str(self)


def get_device_type(uid):
    """
    The top 16 bits of UID.
    """
    return int(uid >> 72)


def get_year(uid):
    """
    Bits 71:64 of UID.
    """
    temp = uid >> 64
    return int(temp & 0xFF)


def get_id(uid):
    """
    Bits 63:0 of UID.
    """
    return uid & 0xFFFFFFFFFFFFFFFF


def checksum(data):
    """
    Compute a checksum for DATA.
    """
    # Remove this later after development
    assert isinstance(data, bytearray), "data must be a bytearray"

    chk = data[0]
    for i in range(1, len(data)):
        chk ^= data[i]
    return chk


def send(serial_conn, message):
    """
    Send MESSAGE over SERIAL_CONN.
    """
    m_buff = message.to_bytes()
    chk = checksum(m_buff)
    m_buff.append(chk)
    encoded = cobs_encode(m_buff)
    out_buf = bytearray([0x00, len(encoded)]) + encoded
    serial_conn.write(out_buf)


def encode_params(device_id, params):
    """
    Encode a list of parameters into a bitmask.

    Parameters:
        device_id  - a device type id (not uid)
        params     - a list of parameter names
    Returns:
        An int representing the bitmask of a set of parameters.
    """
    param_nums = [PARAM_MAP[device_id][name][0] for name in params]
    entries = [1 << num for num in param_nums]
    mask = 0
    for entry in entries:
        mask = mask | entry
    return mask


def decode_params(device_id, params_bitmask):
    """
    Decode PARAMS_BITMASK.

    Parameters:
        device_id      - a device type id (not uid)
        params_bitmask - the set of parameters in binary form
    Returns:
        A list of names symbolizing the encoded parameters.
    """
    converted_params = []
    for param_count in range(16):
        if (params_bitmask & (1 << param_count)) > 0:
            converted_params.append(param_count)
    named_params = []
    for param in converted_params:
        if param >= len(DEVICES[device_id]["params"]):
            break
        named_params.append(DEVICES[device_id]["params"][param]["name"])
    return named_params


def format_string(device_id, params):
    """
    A string representation of the types of PARAMS.
    """
    param_type = [PARAM_MAP[device_id][name][1] for name in params]

    type_string = ''
    for ptype_key in param_type:
        type_string += PARAM_TYPES[ptype_key]
    return type_string


def make_ping():
    """ Makes and returns Ping message."""
    payload = bytearray()
    message = HibikeMessage(MESSAGE_TYPES["Ping"], payload)
    return message


def make_disable():
    """ Makes and returns a Disable message."""
    payload = bytearray()
    message = HibikeMessage(MESSAGE_TYPES["Disable"], payload)
    return message


def make_heartbeat_response(heartbeat_id=0):
    """ Makes and returns HeartBeat message."""
    payload = bytearray(struct.pack('<B', heartbeat_id))
    message = HibikeMessage(MESSAGE_TYPES["HeartBeatResponse"], payload)
    return message


def make_subscription_request(device_id, params, delay):
    """
    Makes and returns SubscriptionRequest message.

    Looks up config data about the specified
    device_id to properly construct the message.
    Parameters:
        device_id - a device type id (not uid).
        params    - an iterable of param names
        delay     - the delay in milliseconds
    """
    params_bitmask = encode_params(device_id, params)
    temp_payload = struct.pack('<HH', params_bitmask, delay)
    payload = bytearray(temp_payload)
    message = HibikeMessage(MESSAGE_TYPES["SubscriptionRequest"], payload)
    return message


def make_subscription_response(device_id, params, delay, uid):
    """
    Makes and returns SubscriptionResponse message.

    Looks up config data about the specified
    device_id to properly construct the message.
    Parameters:
        device_id - a device type id (not uid).
        params    - an iterable of param names
        delay     - the delay in milliseconds
        uid       - the uid
    """
    params_bitmask = encode_params(device_id, params)
    device_type = get_device_type(uid)
    year = get_year(uid)
    id_num = get_id(uid)
    temp_payload = struct.pack(
        "<HHHBQ", params_bitmask, delay, device_type, year, id_num)
    payload = bytearray(temp_payload)
    message = HibikeMessage(MESSAGE_TYPES["SubscriptionResponse"], payload)

    return message


def make_device_read(device_id, params):
    """
    Makes and returns DeviceRead message.

    Looks up config data about the specified
    device_id to properly construct the message.
    Parameters:
        device_id - a device type id (not uid).
        params    - an iterable of param names
    """
    params_bitmask = encode_params(device_id, params)
    temp_payload = struct.pack('<H', params_bitmask)
    payload = bytearray(temp_payload)
    message = HibikeMessage(MESSAGE_TYPES["DeviceRead"], payload)
    return message


def make_device_write(device_id, params_and_values):
    """
    Makes and returns DeviceWrite message.
    If all the params cannot fit, it will fill as many as it can.

    Looks up config data about the specified
    device_id to properly construct the message.
    Parameters:
        device_id         - a device type id (not uid).
        params_and_values - an iterable of param (name, value) tuples
    """
    params_and_values = sorted(
        params_and_values, key=lambda x: PARAM_MAP[device_id][x[0]][0])
    params = [param[0] for param in params_and_values]
    params_bitmask = encode_params(device_id, params)
    values = [param[1] for param in params_and_values]

    type_string = '<H' + format_string(device_id, params)
    temp_payload = struct.pack(type_string, params_bitmask, *values)
    payload = bytearray(temp_payload)
    message = HibikeMessage(MESSAGE_TYPES["DeviceWrite"], payload)
    return message


def make_device_data(device_id, params_and_values):
    """
    Makes and returns DeviceData message.

    If all the params cannot fit, it will fill as many as it can.
    Looks up config data about the specified
    device_id to properly construct the message.
    Parameters:
        device_id         - a device type id (not uid).
        params_and_values - an iterable of param (name, value) tuples
    """
    params = [param_tuple[0] for param_tuple in params_and_values]
    params_bitmask = encode_params(device_id, params)
    values = [param_tuple[1] for param_tuple in params_and_values]

    type_string = '<H' + format_string(device_id, params)

    temp_payload = struct.pack(type_string, params_bitmask, *values)
    payload = bytearray(temp_payload)

    message = HibikeMessage(MESSAGE_TYPES["DeviceData"], payload)
    return message


def make_error(error_code):
    """ Makes and returns Error message."""
    temp_payload = struct.pack('<B', error_code)
    payload = bytearray(temp_payload)
    message = HibikeMessage(MESSAGE_TYPES["Error"], payload)
    return message


def parse_subscription_response(msg):
    """
    Expand MSG into its constituent parts.
    """
    assert msg.get_message_id() == MESSAGE_TYPES["SubscriptionResponse"]
    payload = msg.get_payload()
    assert len(payload) == 15
    params, delay, device_id, year, id_num = struct.unpack("<HHHBQ", payload)
    params = decode_params(device_id, params)
    uid = (device_id << 72) | (year << 64) | id_num
    return (params, delay, uid)


def decode_device_write(msg, device_id):
    """
    Decode a DeviceWrite packet, MSG, into its constituent parts.
    """
    assert msg.get_message_id() == MESSAGE_TYPES["DeviceWrite"]
    payload = msg.get_payload()
    assert len(payload) >= 2
    params, = struct.unpack("<H", payload[:2])
    params = decode_params(device_id, params)
    struct_format = "<" + format_string(device_id, params)
    values = struct.unpack(struct_format, payload[2:])
    return list(zip(params, values))


def parse_device_data(msg, device_id):
    """
    Decode a DeviceData packet, MSG, into its constituent parts.
    """
    assert msg.get_message_id() == MESSAGE_TYPES["DeviceData"]
    payload = msg.get_payload()
    assert len(payload) >= 2
    params, = struct.unpack("<H", payload[:2])
    params = decode_params(device_id, params)
    struct_format = "<" + format_string(device_id, params)
    values = struct.unpack(struct_format, payload[2:])
    return list(zip(params, values))


def parse_bytes(msg_bytes):
    """
    Parse MSG_BYTES into a HibikeMessage, or None if they form an invalid packet.
    """
    if len(msg_bytes) < 2:
        return None
    cobs_frame, message_size = struct.unpack('<BB', msg_bytes[:2])
    if cobs_frame != 0 or len(msg_bytes) < message_size + 2:
        return None
    message = cobs_decode(msg_bytes[2:message_size + 2])

    if len(message) < 2:
        return None
    message_id, payload_length = struct.unpack('<BB', message[:2])
    if len(message) < 2 + payload_length + 1:
        return None
    payload = message[2:2 + payload_length]
    chk = struct.unpack(
        '<B', message[2 + payload_length:2 + payload_length + 1])[0]
    if chk != checksum(message[:-1]):
        return None
    return HibikeMessage(message_id, payload)


def blocking_read_generator(serial_conn, stop_event=None):
    """
    Yield packets from SERIAL_CONN, stopping if STOP_EVENT exists
    and is set.
    """
    zero_byte = bytes([0])
    packets_buffer = bytearray()
    while stop_event is None or not stop_event.is_set():

        # Wait for a 0 byte to appear
        while packets_buffer.find(zero_byte) == -1:
            new_bytes = serial_conn.read(max(1, serial_conn.inWaiting()))
            packets_buffer.extend(new_bytes)

        # Truncate incomplete packets at start of buffer
        packets_buffer = packets_buffer[packets_buffer.find(zero_byte):]

        # Attempt to parse a packet
        packet = parse_bytes(packets_buffer)

        if packet != None:
            # Chop off a byte so we don't output this packet again
            packets_buffer = packets_buffer[1:]
            yield packet
        else:
            # If there's another packet in the buffer
            # we can safely jump to it for the next iteration
            if packets_buffer.count(zero_byte) > 1:
                new_packet = packets_buffer[1:].find(zero_byte) + 1
                packets_buffer = packets_buffer[new_packet:]
            # Otherwise, there might be more incoming bytes for the current packet,
            # so we do a blocking read and try again
            else:
                new_bytes = serial_conn.read(max(1, serial_conn.inWaiting()))
                packets_buffer.extend(new_bytes)


def blocking_read(serial_conn):
    """
    Read a list of packets from SERIAL_CONN, blocking until a complete packet is received.
    """
    zero_byte = bytes([0])
    packets = bytearray()
    while packets.find(zero_byte) == -1:
        packets.extend(serial_conn.read(max(1, serial_conn.inWaiting())))

    # Truncate incomplete packets at start of buffer
    packets = packets[packets.find(zero_byte):]

    # Read until we have no incomplete packets
    last_zero = packets.rfind(zero_byte)
    if last_zero == len(packets) - 1:
        packets.extend(serial_conn.read(size=1))
    last_message_size = packets[last_zero + 1]

    # -2 because payload length and zero byte are not counted
    received_payload = len(packets) - last_zero - 2

    # We don't need to account for the checksum because it is part of the payload
    packets.extend(serial_conn.read(last_message_size - received_payload))

    packet_list = []
    while packets:
        next_packet = packets[1:].find(zero_byte)
        if next_packet == -1:
            next_packet = len(packets)
        else:
            # because we searched in packets[1:] instead of packets
            next_packet += 1
        packet = parse_bytes(packets)
        if packet != None:
            packet_list.append(packet)
        packets = packets[next_packet:]

    return packet_list

# constructs a new object Message by continually reading from input
# Uses dictionary to figure out length of data to know how many bytes to read
# Returns:
    # None if no message
    # -1 if checksum does not match
    # Otherwise returns a new HibikeMessage with message contents


def read(serial_conn):
    """
    Continually read from SERIAL_CONN, attempting to construct an HibikeMessage.

    Returns:
        None if no message.
        -1 if checksum doesn't match.
        Otherwise, a new HibikeMessage with contents.
    """
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
    message_id, payload_length = struct.unpack('<BB', message[:2])
    if len(message) < 2 + payload_length+ 1:
        return None
    payload = message[2:2 + payload_length]

    chk = struct.unpack(
        '<B', message[2 + payload_length:2 + payload_length+ 1])[0]
    if chk != checksum(message[:-1]):
        print(chk, checksum(message[:-1]), list(message))
        return -1

    return HibikeMessage(message_id, payload)


def cobs_encode(data):
    """
    COBS-encode DATA.
    """
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
    """
    Decode COBS-encoded DATA.
    """
    output = bytearray()
    index = 0
    while index < len(data):
        block_size = data[index] - 1
        index += 1
        if index + block_size > len(data):
            return bytearray()
        output.extend(data[index:index + block_size])
        index += block_size
        if block_size + 1 < 255 and index < len(data):
            output.append(0)
    return output


class HibikeMessageException(Exception):
    """
    An exception caused by a Hibike message.
    """
    pass
# Config file helper functions


def device_name_to_id(name):
    """
    Turn NAME into its corresponding device ID.
    """
    for device in DEVICES.values():
        if device["name"] == name:
            return device["id"]
    raise HibikeMessageException("Invalid device name: %s" % name)


def device_id_to_name(device_id):
    """
    Turn DEVICE_ID into its corresponding device name.
    """
    for device in DEVICES.values():
        if device["id"] == device_id:
            return device["name"]
    raise HibikeMessageException("Invalid device id: %d" % id)


def uid_to_device_name(uid):
    """
    Turn UID into its corresponding device name.
    """
    return device_id_to_name(uid_to_device_id(uid))


def uid_to_device_id(uid):
    """
    Turn UID into its corresponding device ID.
    """
    return uid >> 72


def all_params_for_device_id(device_id):
    """
    Get all parameters that a device with ID DEVICE_ID takes.
    """
    return list(PARAM_MAP[device_id].keys())


def readable(device_id, param):
    """
    Check if the device at DEVICE_ID's parameter PARAM is readable.
    """
    return PARAM_MAP[device_id][param][2]


def writable(device_id, param):
    """
    Check if the device at DEVICE_ID's parameter PARAM is writeable.
    """
    return PARAM_MAP[device_id][param][3]
