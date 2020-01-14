import abc
import asyncio
import dataclasses
import datetime
import threading
from typing import Any, Mapping

from schema import And, Schema, Use, Optional
import structlog
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass
import zmq
from zmq.asyncio import Context, Socket

from runtime.messaging import routing


LOGGER = structlog.get_logger()
SOCKET_SCHEMA = Schema({
    'socket_type': And(Use(str.upper), Use(routing.SOCKET_TYPES.get)),
    'address': str,
    Optional('bind', default=False): Use(bool),
    Optional('send_timeout'): Use(float),
    Optional('recv_timeout'): Use(float),
})


@dataclasses.dataclass
class Service(abc.ABC):
    zmq_context: Context = dataclasses.field(default_factory=Context)
    connections: Mapping[str, routing.Connection] = dataclasses.field(default_factory=dict)

    def __call__(self, config, *args, **kwargs):
        asyncio.run(self.bootstrap(config, *args, **kwargs))

    def create_connections(self, sockets):
        for name, socket_conf in sockets.items():
            LOGGER.debug('Creating connection', name=name, **socket_conf)
            socket_conf = SOCKET_SCHEMA.validate(socket_conf)
            socket = routing.make_socket(**socket_conf, context=self.zmq_context)
            self.connections[name] = routing.Connection(socket)

    async def bootstrap(self, config):
        self.create_connections(config['sockets'])
        await self.main(config['config'])

    @abc.abstractmethod
    async def main(self, config):
        pass
