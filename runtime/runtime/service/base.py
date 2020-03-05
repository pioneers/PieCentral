import abc
import asyncio
import dataclasses
import threading
import typing

from schema import And, Optional, Or, Schema, Use
import zmq

from runtime.monitoring import log
from runtime.util import POSITIVE_INTEGER, VALID_NAME


@dataclasses.dataclass(init=False)
class Service(abc.ABC):
    """
    A service consists of one or more daemon processes.

    Unless interrupted, every process should run indefinitely, communicating
    with other processes over shared memory or ZMQ sockets, which primarily use
    TCP or UNIX transports. Every process can also forward its log records and
    handle UNIX signals to shutdown itself gracefully.

    Attributes::
        config_schema (dict): Base service configuration schema.

    Note::
        We need separate `udp_context` and `stream_context` for now because
        `zmq.asyncio.Context` does not yet support RADIO/DISH sockets.

    References::
        https://github.com/zeromq/libzmq/issues/2941
    """
    config: dict
    log_records: typing.Optional[asyncio.Queue] = None

    config_schema = {
        Optional('replicas', default=1): POSITIVE_INTEGER,
        Optional('daemon', default=True): bool,
        Optional('sockets', default={}): {
            VALID_NAME: {
                'socket_type': And(Use(str.upper),
                                   Use(lambda socket_type: getattr(zmq, socket_type))),
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
        """
        Process entry point.

        Names the main thread after the service and starts the asyncio event loop.
        """
        threading.current_thread().name = type(self).__name__.lower()
        asyncio.run(self.bootstrap(), debug=self.config['debug'])

    async def bootstrap(self):
        """ Initialize log record forwarding and signal handlers. """
        self.log_records = asyncio.Queue()
        asyncio.create_task(log.drain_logs(self.log_records))
        # TODO: handle Unix signals
        # (https://docs.python.org/3/library/asyncio-eventloop.html#id13)
        await self.main()

    @abc.abstractmethod
    async def main(self):
        """ Service main. """
