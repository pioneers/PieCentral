import abc
import asyncio
import dataclasses
import datetime
from typing import Any, Mapping

from schema import And, Schema, Use, Optional
import structlog
import zmq
from zmq.asyncio import Context, Socket

from runtime.messaging import routing


SOCKETS_SCHEMA = Schema(And(Use(dict), {
    'socket_type': And(Use(str.upper), Use(routing.SOCKET_TYPES.get)),
    'address': str,
    Optional('bind', default=False): bool,
}))


@dataclasses.dataclass
class Service(abc.ABC):
    zmq_context: Context = dataclasses.field(default_factory=Context)
    connections: Mapping[str, routing.Connection] = dataclasses.field(default_factory=dict)
    logger: structlog.BoundLoggerBase = dataclasses.field(default_factory=structlog.get_logger)

    def __call__(self, *args, **kwargs):
        asyncio.run(self.bootstrap(*args, **kwargs))

    def create_connections(self, sockets):
        for name, config in sockets.items():
            config = SOCKETS_SCHEMA.validate(config)
            socket = routing.make_socket(**config, context=self.zmq_context)
            self.connections[name] = routing.Connection(socket)

    async def bootstrap(self, *, sockets=None, proxies=None, config=None):
        self.create_connections(sockets)
        await self.main(config)

    @abc.abstractmethod
    async def main(self, config):
        pass
