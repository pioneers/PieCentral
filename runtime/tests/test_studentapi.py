import asyncio
import ctypes
import os
import tempfile

import yaml
import pytest

from runtime.game.studentapi import (
    DeviceAliasManager,
    safe,
    Actions,
    Mode,
    Match,
    Gamepad,
    Robot,
)
from runtime.messaging.device import DeviceBuffer, SmartSensorStructure
from runtime.monitoring import log
from runtime.util.exception import RuntimeExecutionError


log.configure(*log.get_processors(pretty=False), level='CRITICAL')

EXISTING_ALIASES = """
left_motor:   '12345678'
right_motor:  '01234567'
center_motor: 12345678
""".strip()


@pytest.fixture
def aliases():
    aliases_file = tempfile.NamedTemporaryFile()
    aliases_file.write(EXISTING_ALIASES.encode('utf-8'))
    aliases_file.flush()
    aliases = DeviceAliasManager(aliases_file.name)
    yield aliases
    try:
        aliases_file.close()
    except FileNotFoundError:
        pass


@pytest.fixture
def gamepad():
    gamepad_type = SmartSensorStructure.make_type('Gamepad', 0, [
        SmartSensorStructure.Parameter('button_a', ctypes.c_bool),
        SmartSensorStructure.Parameter('joystick_left_x', ctypes.c_float),
    ])
    buf = bytearray([0])*ctypes.sizeof(gamepad_type)
    device = DeviceBuffer(buf, gamepad_type.from_buffer(buf))
    device.struct.set_current('button_a', False)
    device.struct.set_current('joystick_left_x', 1.234)
    return Gamepad({'gamepad-0': device, 'gamepad-1': device}, Mode.TELEOP)


@pytest.fixture
def robot():
    pass


@pytest.mark.asyncio
async def test_load_existing_aliases(aliases):
    assert len(aliases) == 0
    await aliases.load_existing_aliases()
    assert len(aliases) == 3
    assert aliases['left_motor'] == aliases['center_motor'] == '12345678'
    assert aliases['right_motor'] == '01234567'


@pytest.mark.asyncio
async def test_load_existing_aliases_missing(aliases):
    os.unlink(aliases.filename)
    assert not os.path.exists(aliases.filename)
    await aliases.load_existing_aliases()
    assert len(aliases) == 0


@pytest.mark.asyncio
async def test_load_existing_aliases_bad(aliases):
    with open(aliases.filename, 'w+') as aliases_file:
        aliases_file.write('')
    await aliases.load_existing_aliases()
    assert len(aliases) == 0


@pytest.mark.asyncio
async def test_persist_aliases_set(aliases):
    aliases['motor'] = '00000000'
    await asyncio.sleep(0.1)
    with open(aliases.filename, 'r') as aliases_file:
        assert yaml.safe_load(aliases_file.read()) == {'motor': '00000000'}

    aliases['motor'] = 1
    await asyncio.sleep(0.1)
    with open(aliases.filename, 'r') as aliases_file:
        assert yaml.safe_load(aliases_file.read()) == {'motor': '1'}


@pytest.mark.asyncio
async def test_persist_aliases_del(aliases):
    aliases['motor'] = '00000000'
    del aliases['motor']
    await asyncio.sleep(0.1)
    with open(aliases.filename, 'r') as aliases_file:
        assert yaml.safe_load(aliases_file.read()) == {}


def test_safe():
    @safe
    def api(fail=False):
        if fail:
            raise RuntimeExecutionError('Failure')
        return 1
    assert api() == 1
    assert api(fail=True) is None


@pytest.mark.asyncio
async def test_sleep(mocker):
    mocker.patch('asyncio.sleep')
    await Actions.sleep(1.234)
    asyncio.sleep.assert_called_once_with(1.234)


def test_gamepad_get(gamepad):
    assert gamepad.get_value('button_a') is False
    assert abs(gamepad.get_value('joystick_left_x') - 1.234) <= 1e-6
    assert gamepad.get_value('button_a', 1) is False
    assert abs(gamepad.get_value('joystick_left_x') - 1.234) <= 1e-6


def test_gamepad_bad(gamepad):
    assert gamepad.get_value('button_a', 2) is None
    assert gamepad.get_value('bad_field') is None


def test_gamepad_get_auto(gamepad):
    gamepad.mode = Mode.AUTO
    assert gamepad.get_value('button_a') is None
