import asyncio
from concurrent.futures import ThreadPoolExecutor
import dataclasses

from schema import And, Optional
import structlog
import zmq
import zmq.asyncio

from runtime.service.base import Service
from runtime.messaging.routing import Connection
from runtime.util import POSITIVE_INTEGER, VALID_NAME
from runtime.util.exception import EmergencyStopException


LOGGER = structlog.get_logger()


@dataclasses.dataclass
class BrokerService(Service):
    config_schema = dict(Service.config_schema)
    config_schema.update({
        Optional('max_workers', default=5): POSITIVE_INTEGER,
        Optional('proxies', default={}): {
            VALID_NAME: {
                'frontend': VALID_NAME,
                'backend': VALID_NAME,
            }
        },
    })

    def serve_proxy(self, proxy):
        frontend, backend = proxy['frontend'], proxy['backend']
        frontend_socket = self.connections[frontend].socket
        backend_socket = self.connections[backend].socket
        LOGGER.debug('Serving proxy', frontend=frontend, backend=backend)
        zmq.proxy(frontend_socket, backend_socket)  # FIXME

    async def main(self):
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as thread_pool:
            loop = asyncio.get_running_loop()
            proxies = [loop.run_in_executor(thread_pool, self.serve_proxy, proxy)
                       for proxy in self.config['proxies'].values()]
            await asyncio.wait(proxies)
