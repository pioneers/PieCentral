import asyncio
from concurrent.futures import ThreadPoolExecutor

import zmq
import zmq.asyncio

from runtime.service.base import Service
from runtime.messaging.routing import Connection
from runtime.util.exception import EmergencyStopException


class BrokerService(Service):
    def serve_proxy(self, proxy):
        frontend, backend = proxy['frontend'], proxy['backend']
        frontend_socket = self.connections[frontend].socket
        backend_socket = self.connections[backend].socket
        self.logger.debug('Serving proxy', frontend=frontend, backend=backend)
        zmq.proxy(frontend_socket, backend_socket)  # FIXME

    async def main(self, config):
        with ThreadPoolExecutor(max_workers=config['max_workers']) as thread_pool:
            event_loop = asyncio.get_event_loop()
            proxies = [event_loop.run_in_executor(thread_pool, self.serve_proxy, proxy)
                       for proxy in config['proxies'].values()]
            await asyncio.wait(proxies)
