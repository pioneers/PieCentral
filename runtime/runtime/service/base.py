import abc
import asyncio
import dataclasses
import datetime
import threading
from typing import Any, Mapping

from schema import And, Optional, Or, Schema, Use
import structlog
import zmq
from zmq.asyncio import Context, Socket

from runtime.messaging.routing import ConnectionManager
from runtime.util import POSITIVE_INTEGER, VALID_NAME


LOGGER = structlog.get_logger()


@dataclasses.dataclass(init=False)
class Service(abc.ABC):
    """
    Note::
        We need separate `udp_context` and `stream_context` for now because
        `zmq.asyncio.Context` does not yet support RADIO/DISH sockets.

    References::
        https://github.com/zeromq/libzmq/issues/2941
    """
    config: Any
    connections: ConnectionManager = dataclasses.field(default_factory=ConnectionManager)

    config_schema = {
        Optional('replicas', default=1): POSITIVE_INTEGER,
        Optional('daemon', default=True): bool,
        Optional('retry'): list,  # FIXME
        Optional('sockets', default={}): {
            VALID_NAME: {
                'socket_type': Or(Use(str.upper), int),
                'address': str,
                Optional('bind', default=False): bool,
                Optional('send_timeout'): Use(float),
                Optional('recv_timeout'): Use(float),
                Optional('group', default=b''): (lambda group: len(group) < 16),
            }
        },
    }

    @classmethod
    def get_config_schema(cls) -> Schema:
        return Schema(cls.config_schema)

    def __call__(self):
        threading.current_thread().name = self.__class__.__name__.lower()
        asyncio.run(self.bootstrap())

    async def bootstrap(self):
        for name, socket_config in self.config['sockets'].items():
            self.connections.open_connection(name, socket_config)
        # TODO: handle Unix signals (https://docs.python.org/3/library/asyncio-eventloop.html#id13)
        try:
            await self.main()
        finally:
            self.connections.clear()

    @abc.abstractmethod
    async def main(self):
        pass
