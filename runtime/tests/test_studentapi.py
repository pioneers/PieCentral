import asyncio
import tempfile

import yaml
import pytest

from runtime.game.studentapi import (
    DeviceAliasManager,
)
from runtime.util.exception import RuntimeBaseException


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
    aliases_file.close()


@pytest.mark.asyncio
async def test_load_existing_aliases(aliases):
    assert len(aliases) == 0
    await aliases.load_existing_aliases()
    assert len(aliases) == 3
    assert aliases['left_motor'] == aliases['center_motor'] == '12345678'
    assert aliases['right_motor'] == '01234567'


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
