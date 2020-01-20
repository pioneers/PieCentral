# distutils: language = c++

import ctypes
cimport cython
from libcpp cimport bool
from libcpp.string cimport string
from libc.stdint cimport uint8_t, uint16_t

from cobs import cobs

from runtime.messaging.device import DeviceStructure, SmartSensorUID, get_field_bytes
from runtime.util.exception import RuntimeBaseException


cpdef Py_ssize_t MAX_PARAMETERS = 16


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
    UNEXPECTED_DELIM  = 0xFD
    BAD_CHECKSUM      = 0xFE
    GENERIC           = 0xFF


cpdef uint8_t checksum(string buf) nogil:
    cdef uint8_t ctr = 0x00
    for i in range(buf.size()):
        ctr ^= buf[i]
    return ctr


class PacketEncodingException(RuntimeBaseException):
    """ Exception representing a packet encoding/decoding failure. """


@cython.final
@cython.freelist(32)
cdef class Packet:
    cdef readonly MessageType message_id
    cdef readonly string payload

    def __cinit__(self, MessageType message_id, string payload):
        self.message_id, self.payload = message_id, payload

    def __len__(self):
        return self.payload.size()

    def __repr__(self):
        return f'Packet({MessageType(self.message_id).name}, {self.payload})'

    cpdef string encode(self) nogil:
        cdef Py_ssize_t payload_len = self.payload.size()
        cdef string packet
        if self.message_id > 0xFF or payload_len > 0xFF:
            return packet
        packet += (<uint8_t> self.message_id)
        packet += (<uint8_t> payload_len)
        packet += self.payload
        packet += checksum(packet)
        return packet

    @property
    def heartbeat_id(self):
        return self.payload.at(0)

    @property
    def parameter_map(self):
        cdef uint16_t param_map = self.payload.at(1) << 8 | self.payload.at(0)
        return param_map

    @property
    def delay(self):
        cdef uint16_t duration = self.payload.at(3) << 8 | self.payload.at(2)
        return duration

    @property
    def uid(self):
        return SmartSensorUID.from_buffer_copy(self.payload.substr(4, 11))

    @property
    def error_code(self):
        return self.payload.at(0)


cpdef Packet make_ping():
    return Packet(PING, b'')


cpdef Packet make_sub_req():
    cdef string payload
    return Packet(SUB_REQ, payload)


cpdef Packet make_dev_read(sensor_struct):
    cdef string payload = get_field_bytes(sensor_struct, 'read')
    return Packet(DEV_READ, payload)


cpdef Packet make_dev_write(sensor_struct):
    """
    Note::
        The parameter map is not validated for which parameters are actually
        writable.
    """
    cdef string payload = get_field_bytes(sensor_struct, 'write')
    for param in sensor_struct.get_parameters(sensor_struct.write):
        if param.writeable:
            param = getattr(sensor_struct, f'desired_{param.name}')
            payload += <string> get_field_bytes(param, 'value')
    return Packet(DEV_WRITE, payload)


cpdef Packet make_heartbeat_req(uint8_t id = 0):
    cdef string payload
    payload += id
    return Packet(HEARTBEAT_REQ, payload)


cpdef Packet make_heartbeat_res(uint8_t id = 0):
    cdef string payload
    payload += id
    return Packet(HEARTBEAT_RES, payload)


cpdef Packet decode(string packet):
    cdef uint8_t expected_checksum = packet.at(packet.size() - 1)
    cdef uint8_t actual_checksum = checksum(packet.substr(0, packet.size() - 1))
    if actual_checksum != expected_checksum:
        raise PacketEncodingException('Bad checksum',
                                      expected_checksum=expected_checksum,
                                      actual_checksum=actual_checksum,
                                      packet=list(packet))
    cdef Py_ssize_t payload_len = packet.at(1)
    cdef string payload = packet.substr(2, payload_len)
    return Packet(packet.at(0), payload)


async def send(serial_conn, packet, delimeter: bytes = b'\x00'):
    encoded_packet = cobs.encode(packet.encode())
    if len(encoded_packet) > 0xff:
        raise PacketEncodingException('Packet is too large to encode',
                                      packet_len=len(encoded_packet))
    frame = bytearray()
    frame.extend(delimeter)
    frame.append(len(encoded_packet))
    frame.extend(encoded_packet)
    await serial_conn.write_async(frame)


async def recv(serial_conn, delimeter: bytes = b'\x00'):
    frame = await serial_conn.read_until_async(delimeter)
    assert frame.endswith(delimeter)
    if len(frame) < 1 + len(delimeter):
        raise PacketEncodingException('Received empty frame')
    packet_size, packet = frame[0], cobs.decode(frame[1:-len(delimeter)])
    if 1 + packet_size + len(delimeter) != len(frame) or len(packet) < 3:
        raise PacketEncodingException('Bad packet size', frame_size=frame,
                                      frame=list(frame))
    return decode(packet)
