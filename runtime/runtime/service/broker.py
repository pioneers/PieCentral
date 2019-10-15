import asyncio

import zmq
import zmq.asyncio

from runtime.service.base import Service
from runtime.messaging.routing import Connection
from runtime.util.exception import EmergencyStopException


class BrokerService(Service):
    async def main(self, config):
        # while True:
        #     self.raw_sockets['journal_out'].send(b'sdf')
        #     await asyncio.sleep(1)

        # zmq.proxy(self.raw_sockets['journal_in'], self.raw_sockets['journal_out'])

        # while True:
        #     ping = await self.raw_sockets['journal_in'].recv()
        #     self.logger.debug('Received ping', ping=ping)

        while True:
            self.logger.debug('Hello!')
            await asyncio.sleep(1)
