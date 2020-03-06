import ctypes

from schema import SchemaError
import pytest

from runtime.messaging import device as devlib
from runtime.util.exception import RuntimeBaseException


@pytest.fixture
def device_type():
    return devlib.SmartSensorStructure.make_type('Sensor', 0, [
        devlib.SmartSensorStructure.Parameter('param1', ctypes.c_float),
        devlib.SmartSensorStructure.Parameter('param2', ctypes.c_uint32),
        devlib.SmartSensorStructure.Parameter('param3', ctypes.c_bool),
    ])


@pytest.fixture
def device_buffer(device_type):
    buf = bytearray([0]) * ctypes.sizeof(device_type)
    device = devlib.DeviceBuffer(buf, device_type.from_buffer(buf))
    device.struct.set_current('param1', -1.234)
    device.struct.set_current('param2', 0xdeadbeef)
    device.struct.set_current('param3', True)
    return device


@pytest.fixture
def sensor_uid():
    return devlib.SmartSensorUID(device_type=0x_beef, year=0x11, id=0x_ffff_ffff_ffff_ffff)


def test_param_limit():
    params = [devlib.SmartSensorStructure.Parameter(f'param{i}', ctypes.c_float)
              for i in range(devlib.SmartSensorStructure.MAX_PARAMETERS + 1)]
    with pytest.raises(RuntimeBaseException):
        devlib.SmartSensorStructure.make_type('Sensor', 0, params)
    assert isinstance(devlib.DeviceStructure.make_type('Device', 0, params), type)


def test_get_field_bytes(device_buffer):
    assert devlib.get_field_bytes(device_buffer.struct.current_param1, 'value') == b'\xb6\xf3\x9d\xbf'
    assert devlib.get_field_bytes(device_buffer.struct.current_param2, 'value') == b'\xef\xbe\xad\xde'
    assert devlib.get_field_bytes(device_buffer.struct.current_param3, 'value') == b'\x01'


def test_uid_to_int(sensor_uid):
    assert sensor_uid.to_int() == 0x_beef_11_ffff_ffff_ffff_ffff


def test_parameter_bitmap_translation(device_buffer):
    get_params = lambda bitmap: {param.name: param.type
                                 for param in device_buffer.struct.get_parameters(bitmap)}
    assert get_params(0b010) == {'param2': ctypes.c_uint32}
    assert get_params(0b111) == {'param1': ctypes.c_float, 'param2': ctypes.c_uint32,
                                 'param3': ctypes.c_bool}


def test_writeonly_param():
    dev_type = devlib.DeviceStructure.make_type('Device', 0, [
        devlib.DeviceStructure.Parameter('param', ctypes.c_int, readable=False, writeable=True)
    ])
    assert set(dict(dev_type._fields_)) == set(['desired_param'])


def test_device_type_registry():
    params = [{'name': 'param1', 'type': 'float', 'writeable': True},
              {'name': 'param2', 'type': 'bool'}]
    devlib.load_device_types({'smartsensor2': {'Device1': {'id': 1, 'params': params}}})
    devlib.load_device_types({'smartsensor2': {'Device2': {'id': 2, 'params': params}}})
    assert 'smartsensor2' in devlib.DEVICES
    assert set(devlib.DEVICES['smartsensor2']) == set(['Device1', 'Device2'])
    assert set(dict(devlib.get_device_type(device_id=1)._fields_)) == set([
        'current_param1', 'desired_param1', 'current_param2',
    ])

    assert devlib.get_device_type(device_id=1) is devlib.get_device_type(device_name='Device1')
    assert devlib.get_device_type(device_id=2) is devlib.get_device_type(device_name='Device2')
    with pytest.raises(RuntimeBaseException):
        assert devlib.get_device_type(protocol='smartsensor3')


def test_device_type_registry_bad():
    with pytest.raises(SchemaError):
        devlib.load_device_types({'bad protocol name': {}})
    with pytest.raises(SchemaError):
        devlib.load_device_types({'smartsensor': {'bad device name': {}}})
    with pytest.raises(SchemaError):
        dev_config = {'id': 0x10000, 'params': []}  # ID is not 16 bits
        devlib.load_device_types({'smartsensor': {'Device': dev_config}})


def test_device_buffer(device_type):
    assert device_buffer.is_smart_sensor
    assert device_buffer.status == {'device_type': 'Sensor', 'device_uid': ''}


def test_device_buffer_shm(device_type):
    pass
