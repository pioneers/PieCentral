# distutils: language = c++

"""
Runtime module for encoding and decoding Smart Sensor messages.
"""

from libc.stdint cimport uint8_t, uint16_t, uint64_t
from posix.unistd cimport usleep, useconds_t
from libcpp.string cimport string
from runtime.buffer cimport (
    SensorReadBuffer,
    SensorWriteBuffer,
    BinaryRingBuffer,
    MAX_PARAMETERS,
)


cpdef enum MessageType:
    PING          = 0x10
    SUB_REQ       = 0x11
    SUB_RES       = 0x12
    DEV_READ      = 0x13
    DEV_WRITE     = 0x14
    DEV_DATA      = 0x15
    DEV_DISABLE   = 0x16
    HEARTBEAT_REQ = 0x17
    HEARTBEAT_RES = 0x18
    ERROR         = 0xFF


cpdef enum ErrorCode:
    OK                = 0x00
    UNEXPECTED_DELIM  = 0xFD
    BAD_CHECKSUM      = 0xFE
    GENERIC           = 0xFF


cpdef uint8_t compute_checksum(string message) nogil:
    cdef uint8_t checksum = 0
    for i in range(message.size()):
        checksum ^= message[i]
    return checksum


cpdef string build_packet(MessageType type_id, string payload) nogil:
    cdef size_t payload_len = payload.size()
    cdef string message
    if type_id > 0xFF or payload_len > 0xFF:
        return message
    message += (<uint8_t> type_id)
    message += (<uint8_t> payload_len)
    message += payload
    return message


def parse_sub_res():
    pass


cpdef string make_ping() nogil:
    cdef string empty
    return build_packet(PING, empty)


# cdef string make_sub_req(uint16_t params, uint16_t delays) nogil:



# cdef string make_read() nogil:
#     pass
#
#
# cdef string make_write() nogil:
#     pass
#
#
# cdef string make_heartbeat_req() nogil:
#     pass


cdef string make_heartbeat_res(uint8_t id) nogil:
    cdef string payload
    payload.append(1, <char> id)
    return build_packet(HEARTBEAT_RES, payload)


cpdef string append_packet(BinaryRingBuffer write_queue, string packet) nogil:
    packet.append(1, compute_checksum(packet))
    packet = cobs_encode(packet)
    packet.insert(0, 1, <char> packet.size())
    packet.append(1, <char> 0)
    write_queue._extend(packet)
    return packet


cdef void _encode_loop(SensorWriteBuffer buf, BinaryRingBuffer write_queue, useconds_t period_us) nogil:
    cdef uint16_t present
    cdef string payload
    while True:
        present = 0
        payload.clear()
        buf.acquire()
        for i in range(buf.num_params):
            if buf.is_dirty(i):
                present |= (1 << <uint8_t> i)
                payload.append(buf.get_value(i))
                buf.clear_dirty(i)
        buf.release()
        if present:
            payload.insert(0, <const char *> &present, 2)
            append_packet(write_queue, build_packet(DEV_WRITE, payload))
        usleep(period_us)


cdef void parse_data(SensorReadBuffer buf, string payload) nogil:
    # TODO: verify the endianness is correct
    cdef uint16_t present = ((<uint16_t> payload[1]) << 8) | payload[0]
    cdef size_t param_size
    payload = payload.substr(2)
    for i in range(MAX_PARAMETERS):
        if (present >> <uint16_t> i) & 1:
            param_size = buf.get_size(<Py_ssize_t> i)
            buf.set_value(<Py_ssize_t> i, payload.substr(0, param_size))
            payload = payload.substr(param_size)


from libc.stdio cimport fprintf, stderr

cdef void _decode_loop(SensorReadBuffer buf, BinaryRingBuffer read_queue, BinaryRingBuffer write_queue) nogil:
    cdef uint8_t frame_len, msg_id, payload_len
    cdef string payload
    while True:
        packet = read_queue._read()
        fprintf(stderr, "%s\n", packet)
        continue

        # checksum = compute_checksum(packet.substr(0, packet.size() - 1))
        # if checksum != packet.at(packet.size() - 1):
        #     continue
        #
        # msg_id = <uint8_t> packet.at(0)
        # payload_len = <uint8_t> packet.at(1)
        # payload = cobs_decode(packet.substr(2, 2 + payload_len))
        # if msg_id == HEARTBEAT_REQ:
        #     append_packet(write_queue, make_heartbeat_res(payload[0]))
        # elif msg_id == HEARTBEAT_RES:
        #     pass
        # elif msg_id == DEV_DATA:
        #     parse_data(buf, payload)
        # elif msg_id == SUB_RES:
        #     pass
        # elif msg_id == ERROR:
        #     pass


cpdef string extract_from_frame(string raw_packet) nogil:
    """ Given a raw COBS-encoded packet, remove the COBS frame and verify the checksum. """
    cdef uint8_t frame_size, expected_checksum
    cdef string packet
    frame_size = raw_packet.at(0)
    if frame_size + 1 != raw_packet.size():
        return packet
    raw_packet = cobs_decode(raw_packet.substr(1, 1 + frame_size))
    if raw_packet.size() < 2:
        return packet
    expected_checksum = raw_packet.at(raw_packet.size() - 1)
    packet = raw_packet.substr(0, raw_packet.size() - 1)
    if expected_checksum != compute_checksum(packet):
        packet.clear()
        return packet
    return packet


def encode_loop(SensorWriteBuffer buf not None, BinaryRingBuffer write_queue not None, useconds_t period_us):
    with nogil:
        _encode_loop(buf, write_queue, period_us)


def decode_loop(SensorReadBuffer buf not None,
                BinaryRingBuffer read_queue not None,
                BinaryRingBuffer write_queue not None):
    with nogil:
        _decode_loop(buf, read_queue, write_queue)
