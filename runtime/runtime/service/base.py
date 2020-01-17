import abc
import asyncio
import dataclasses
import datetime
import threading
from typing import Any, Mapping

from schema import And, Optional, Schema, Use
import structlog
import zmq
from zmq.asyncio import Context, Socket

from runtime.messaging import routing
from runtime.util import POSITIVE_INTEGER, VALID_NAME


LOGGER = structlog.get_logger()


@dataclasses.dataclass(init=False)
class Service(abc.ABC):
    config: Any
    zmq_context: Context = dataclasses.field(default_factory=Context)
    connections: Mapping[str, routing.Connection] = dataclasses.field(default_factory=dict)

    config_schema = {
        Optional('replicas', default=1): POSITIVE_INTEGER,
        Optional('daemon', default=True): bool,
        Optional('retry'): list,  # FIXME
        Optional('sockets', default={}): {
            VALID_NAME: {
                'socket_type': And(Use(str.upper), Use(routing.SOCKET_TYPES.get)),
                'address': str,
                Optional('bind', default=False): bool,
                Optional('send_timeout'): Use(float),
                Optional('recv_timeout'): Use(float),
            }
        },
    }

    @classmethod
    def get_config_schema(cls) -> Schema:
        return Schema(cls.config_schema)

    def __call__(self):
        asyncio.run(self.bootstrap())

    def create_connections(self):
        for name, socket_conf in self.config['sockets'].items():
            socket = routing.make_socket(**socket_conf, context=self.zmq_context)
            self.connections[name] = routing.Connection(socket)
            LOGGER.debug('Created connection', name=name, **socket_conf)

    async def bootstrap(self):
        self.create_connections()
        # TODO: handle Unix signals (https://docs.python.org/3/library/asyncio-eventloop.html#id13)
        await self.main()

    @abc.abstractmethod
    async def main(self):
        pass
