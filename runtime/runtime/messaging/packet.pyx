# distutils: language = c++

import ctypes
cimport cython
from libcpp cimport bool
from libcpp.string cimport string
from libc.stdint cimport uint8_t, uint16_t

from cobs import cobs

from runtime.util.exception import RuntimeBaseException


# The Smart Sensor protocol uses little Endian byte order (least-significant byte first).
Structure = ctypes.LittleEndianStructure


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


class SmartSensorUID(Structure):
    """
    A Smart Sensor Unique Identifer (UID).

    The UID is effectively a 96-bit integer that encodes Sensor metadata:
      * `device_type`: An integer denoting the type of Sensor. The types are
            given by the Smart Sensor protocol specification.
      * `year`: The year the Sensor is from. 2016 is denoted as year zero.
      * `id`: A randomly generated ID. This ensures the probability of a UID
            collision (two devices of the same type from the same year) is
            negligible.
    """
    _pack_ = 1  # Ensure the fields are byte-aligned (pack as densely as possible)
    _fields_ = [
        ('device_type', ctypes.c_uint16),
        ('year', ctypes.c_uint8),
        ('id', ctypes.c_uint64),
    ]

    def to_int(self) -> int:
        """
        Return an integer representation of this UID.

        Warning::
            Serializing the UID as an integer may fail if the serializer cannot
            represent integers larger than 64 bits (UID is 96 bits).
        """
        return (self.device_type << 72) | (self.year << 64) | self.id


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
        if self.message_id > 0xff or payload_len > 0xff:
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


cpdef Packet make_disable():
    return Packet(DEV_DISABLE, b'')


cpdef Packet make_sub_req(sensor_struct, uint16_t delay):
    cdef string payload
    cdef uint16_t sub_map = sensor_struct.make_subscription()
    payload += (<uint8_t> (sub_map & 0xff))
    payload += (<uint8_t> ((sub_map >> 8) & 0xff))
    payload += (<uint8_t> (delay & 0xff))
    payload += (<uint8_t> ((delay >> 8) & 0xff))
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
