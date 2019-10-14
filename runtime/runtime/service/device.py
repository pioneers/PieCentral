import asyncio

from runtime.service.base import Service
from runtime.util.exception import EmergencyStopException


class DeviceService(Service):
    async def main(self):
        i = 0
        while i < 2:
            self.logger.debug('Sending ping to journal.')
            await self.raw_sockets['journal'].send(b'ping')
            await asyncio.sleep(1)
            i += 1
        raise EmergencyStopException()
