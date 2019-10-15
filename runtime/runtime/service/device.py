import asyncio

from runtime.service.base import Service
from runtime.util.exception import EmergencyStopException


class DeviceService(Service):
    async def main(self):
        while True:
            self.logger.debug('Sending ping to journal.')
            await self.raw_sockets['journal'].send(b'ping')
            await asyncio.sleep(1)
