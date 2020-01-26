import abc
import asyncio
import dataclasses
import threading

from schema import Optional, Or, Schema, Use

from runtime.messaging.routing import ConnectionManager
from runtime.util import POSITIVE_INTEGER, VALID_NAME


@dataclasses.dataclass(init=False)
class Service(abc.ABC):
    """
    Note::
        We need separate `udp_context` and `stream_context` for now because
        `zmq.asyncio.Context` does not yet support RADIO/DISH sockets.

    References::
        https://github.com/zeromq/libzmq/issues/2941
    """
    config: dict
    connections: ConnectionManager = dataclasses.field(default_factory=ConnectionManager)

    config_schema = {
        Optional('replicas', default=1): POSITIVE_INTEGER,
        Optional('daemon', default=True): bool,
        Optional('sockets', default={}): {
            VALID_NAME: {
                'socket_type': Or(Use(str.upper), int),
                'address': Or(str, [str]),
                Optional('bind', default=False): bool,
                Optional('send_timeout'): Use(float),
                Optional('recv_timeout'): Use(float),
                Optional('group', default=b''): (lambda group: len(group) < 16),
            }
        },
        Optional('debug', default=True): bool,
    }

    @classmethod
    def get_config_schema(cls) -> Schema:
        return Schema(cls.config_schema)

    def __call__(self):
        threading.current_thread().name = type(self).__name__.lower()
        asyncio.run(self.bootstrap(), debug=self.config['debug'])

    async def bootstrap(self):
        with self.connections:
            for name, socket_config in self.config['sockets'].items():
                self.connections.open_connection(name, socket_config)
            # TODO: handle Unix signals
            # (https://docs.python.org/3/library/asyncio-eventloop.html#id13)
            await self.main()

    @abc.abstractmethod
    async def main(self):
        pass
