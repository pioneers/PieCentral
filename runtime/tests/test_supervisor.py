import pytest
from runtime.service.base import Service


class MockService(Service):
    async def main(self):
        pass


@pytest.mark.asyncio
async def test_run_subprocess(service: ):
    pass
