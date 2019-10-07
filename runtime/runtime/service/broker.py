import asyncio

import zmq
import zmq.asyncio

from runtime.service.base import Service
from runtime.messaging.routing import Connection


class BrokerService(Service):
    async def main(self):
        raise ValueError('sdf')
        while True:
            self.logger.info('OK!')
            await asyncio.sleep(1)
