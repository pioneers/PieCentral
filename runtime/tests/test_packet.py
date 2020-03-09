import ctypes

import pytest

from runtime.messaging import packet as packetlib
from test_device_messaging import device_type


@pytest.fixture
def struct(device_type):
    buf = bytearray([0]) * ctypes.sizeof(device_type)
    device = device_type.from_buffer(buf)
    device.set_current('param1', -1.234)
    device.set_current('param2', 0xdeadbeef)
    device.set_current('param3', True)
    return device


@pytest.fixture
def sensor_uid():
    return packetlib.SmartSensorUID(device_type=0x_beef, year=0x11, id=0x_ffff_ffff_ffff_ffff)


def test_uid_to_int(sensor_uid):
    assert sensor_uid.to_int() == 0x_beef_11_ffff_ffff_ffff_ffff


def test_get_field_bytes(struct):
    assert packetlib.get_field_bytes(struct.current_param1, 'value') == b'\xb6\xf3\x9d\xbf'
    assert packetlib.get_field_bytes(struct.current_param2, 'value') == b'\xef\xbe\xad\xde'
    assert packetlib.get_field_bytes(struct.current_param3, 'value') == b'\x01'


def test_make_ping():
    assert packetlib.make_ping().encode() == b'\x10\x00\x10'


def test_make_heartbeat_req():
    assert packetlib.make_heartbeat_req(0x00).encode() == b'\x17\x01\x00\x16'
    assert packetlib.make_heartbeat_req(0xff).encode() == b'\x17\x01\xff\xe9'
    with pytest.raises(OverflowError):
        packetlib.make_heartbeat_req(-0x01).encode()
    with pytest.raises(OverflowError):
        packetlib.make_heartbeat_req(0x100).encode()


def test_make_heartbeat_res():
    assert packetlib.make_heartbeat_res(0x00).encode() == b'\x18\x01\x00\x19'
    assert packetlib.make_heartbeat_res(0xff).encode() == b'\x18\x01\xff\xe6'
    with pytest.raises(OverflowError):
        packetlib.make_heartbeat_res(-0x01).encode()
    with pytest.raises(OverflowError):
        packetlib.make_heartbeat_res(0x100).encode()
