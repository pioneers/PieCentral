# distutils: language = c++

"""
Runtime Packet Encoder/Decoder

A low-level API for preparing sensor data to be sent/received over the wire
according to the Smart Sensor protocol specifications (a packet-based protocol).
"""

import ctypes

cimport cython
from libcpp cimport bool
from libcpp.string cimport string
from libc.stdint cimport uint8_t, uint16_t
from cobs import cobs

from runtime.util.exception import RuntimeBaseException


cpdef enum PacketType:
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


def get_field_bytes(structure: ctypes.Structure, field_name: str) -> bytes:
    field_description = getattr(type(structure), field_name)
    field_ref = ctypes.byref(structure, field_description.offset)
    return ctypes.string_at(field_ref, field_description.size)


cpdef uint8_t checksum(string buf) nogil:
    cdef uint8_t ctr = 0x00
    for i in range(buf.size()):
        ctr ^= buf[i]
    return ctr


class PacketEncodingException(RuntimeBaseException):
    """ Exception for packet encoding/decoding failures. """


class PacketTooLarge(PacketEncodingException):
    """ Exception to indicate a packet is too large to encode. """


@cython.final
@cython.freelist(32)
cdef class Packet:
    cdef readonly PacketType type_id
    cdef readonly string payload

    def __cinit__(self, PacketType type_id, string payload):
        self.type_id, self.payload = type_id, payload

    def __len__(self):
        return 3 + self.payload.size()

    def __eq__(self, Packet message):
        return self.type_id == message.type_id and self.payload == message.payload

    def __repr__(self):
        return f'{self.__class__.__name__}({PacketType(self.type_id).name}, {self.payload!r})'

    cpdef string pack(self):
        """ Pack the message into a binary buffer. """
        cdef Py_ssize_t payload_size = self.payload.size()
        cdef string packet
        if self.payload.size() > 0xFF:
            raise PacketTooLarge('Payload is too large', size=self.payload.size())
        packet += (<uint8_t> self.type_id)
        packet += (<uint8_t> self.payload.size())
        packet += self.payload
        packet += checksum(packet)
        return packet

    cpdef string encode(self):
        """ Encode the message as a packet. """
        cdef string packet
        cdef string message = cobs.encode(self.pack())
        if message.size() > 0xFF:
            raise PacketTooLarge('Packet is too large', size=message.size())
        packet += (<uint8_t> 0x00)
        packet += (<uint8_t> message.size())
        packet += message
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
        return self.payload.substr(4, 11)

    @property
    def error_code(self):
        return self.payload.at(0)

    @classmethod
    def unpack(self, string packet):
        if packet.size() < 3:
            raise PacketEncodingException('Packet is too small')
        cdef uint8_t expected_checksum = packet.at(packet.size() - 1)
        cdef uint8_t actual_checksum = checksum(packet.substr(0, packet.size() - 1))
        if actual_checksum != expected_checksum:
            raise PacketEncodingException('Invalid checksum',
                                          expected_checksum=expected_checksum,
                                          actual_checksum=actual_checksum,
                                          packet=packet)
        cdef Py_ssize_t payload_len = packet.at(1)
        return Packet(packet.at(0), packet.substr(2, payload_len))

    @classmethod
    def decode(cls, string buffer):
        if not 2 <= buffer.size() <= 2 + 0xFF:
            raise PacketEncodingException('Packet is too small or too large')
        assert buffer.at(buffer.size() - 1) == 0x00
        cdef uint8_t packet_size = buffer.at(0)
        if 2 + packet_size > <uint8_t> buffer.size():
            raise PacketEncodingException('Packet is too small')
        cdef string packet = cobs.decode(buffer.substr(1, packet_size))
        return cls.unpack(packet)


cpdef Packet make_ping():
    return Packet(PING, b'')


cpdef Packet make_disable():
    return Packet(DEV_DISABLE, b'')


cpdef Packet make_sub_req(uint16_t subscription, uint16_t delay):
    cdef string payload
    payload += subscription & 0xFF
    payload += (subscription >> 8) & 0xFF
    payload += delay & 0xFF
    payload += (delay >> 8) & 0xFF
    return Packet(SUB_REQ, payload)


cpdef Packet make_dev_read(uint16_t read):
    cdef string payload
    payload += read & 0xFF
    payload += (read >> 8) & 0xFF
    return Packet(DEV_READ, payload)


# cpdef Packet make_dev_write(sensor_struct):
#     """
#     Note::
#         The parameter map is not validated for which parameters are actually
#         writable.
#     """
#     cdef string payload = get_field_bytes(sensor_struct, 'write')
#     for param in sensor_struct.get_parameters(sensor_struct.write):
#         if param.writeable:
#             param = getattr(sensor_struct, f'desired_{param.name}')
#             payload += <string> get_field_bytes(param, 'value')
#     return Packet(DEV_WRITE, payload)


cpdef Packet make_heartbeat_req(uint8_t heartbeat_id = 0):
    cdef string payload
    payload += heartbeat_id
    return Packet(HEARTBEAT_REQ, payload)


cpdef Packet make_heartbeat_res(uint8_t heartbeat_id = 0):
    cdef string payload
    payload += heartbeat_id
    return Packet(HEARTBEAT_RES, payload)
