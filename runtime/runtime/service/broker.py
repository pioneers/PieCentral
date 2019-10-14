import asyncio

import zmq
import zmq.asyncio

from runtime.service.base import Service
from runtime.messaging.routing import Connection
from runtime.util.exception import EmergencyStopException


class BrokerService(Service):
    async def main(self):
        while True:
            ping = await self.raw_sockets['journal_in'].recv()
            self.logger.debug('Received ping', ping=ping)
