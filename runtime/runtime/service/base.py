import abc
import asyncio
import dataclasses
import datetime
from typing import Any, Mapping

import structlog
import zmq
from zmq.asyncio import Context, Socket

from runtime.messaging.routing import make_socket


@dataclasses.dataclass
class Service(abc.ABC):
    config: Any
    zmq_context: Context = dataclasses.field(default_factory=Context)
    raw_sockets: Mapping[str, Socket] = dataclasses.field(default_factory=dict)
    logger: structlog.BoundLoggerBase = dataclasses.field(default_factory=structlog.get_logger)
    shutdown_timeout: datetime.timedelta = datetime.timedelta(seconds=10)

    def __call__(self):
        asyncio.run(self.bootstrap())

    async def bootstrap(self):
        for name, socket_config in self.config['sockets'].items():
            socket_config['socket_type'] = ({'pub': zmq.PUB, 'sub': zmq.SUB})[socket_config['socket_type']]
            self.raw_sockets[name] = make_socket(self.zmq_context, **socket_config)
        await self.main()

    @abc.abstractmethod
    async def main(self):
        pass
