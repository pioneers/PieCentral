import ctypes

import pytest

from runtime.messaging import device as devlib
from runtime.util.exception import RuntimeBaseException


@pytest.fixture
def device_type():
    return SmartSensorStructure.make_type()


@pytest.fixture
def device_buffer(device_type):
    return


def test_param_limit():
    params = [devlib.SmartSensorStructure.Parameter(f'param{i}', ctypes.c_float)
              for i in range(devlib.SmartSensorStructure.MAX_PARAMETERS + 1)]
    with pytest.raises(RuntimeBaseException):
        devlib.SmartSensorStructure.make_type('Sensor', 0, params)
    assert isinstance(devlib.DeviceStructure.make_type('Device', 0, params), type)


def test_load_device_types():
    dev_config = {'id': 0x1234, 'params': [{'name': 'param', 'type': 'float', 'lower': 0}]}
    devlib.load_device_types({'smartsensor2': {'Device1': dev_config}})
    devlib.load_device_types({'smartsensor2': {'Device2': dev_config}})
    assert 'smartsensor2' in devlib.DEVICES
    assert set(devlib.DEVICES['smartsensor2']) == set(['Device1', 'Device2'])
    # assert set(devlib.DEVICES['smartsensor2']['Device1']._fields_) ==


def test_load_device_types_bad():
    pass
