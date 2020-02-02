import asyncio
import dataclasses
import logging
import threading
from typing import Optional, Tuple

import msgpack
import rapidjson
import structlog
import structlog.processors
import structlog.stdlib
import zmq
import zmq.asyncio
import zmq.devices

from runtime.messaging.routing import Connection


FRONTEND_ADDR: str = None


@dataclasses.dataclass
class LogCapture:
    loop: Optional[asyncio.AbstractEventLoop] = None
    records: Optional[asyncio.Queue] = None
    thread_id: Optional[int] = None

    def __call__(self, _logger, _method, event):
        if self.connected:
            if self.thread_id == threading.get_ident():
                call_soon = self.loop.call_soon
            else:
                call_soon = self.loop.call_soon_threadsafe
            call_soon(self.records.put_nowait, event.copy())
        return event

    def connect(self, records: asyncio.Queue):
        self.loop, self.records = asyncio.get_running_loop(), records
        self.thread_id = threading.get_ident()

    @property
    def connected(self):
        return bool(self.loop and self.records and self.thread_id)


def get_logger(capture: LogCapture, *args, **kwargs):
    return structlog.get_logger(*args, processors=get_processors(capture), **kwargs)


def get_processors(*extra_processors, pretty: bool = True):
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    processors.extend(extra_processors)

    if pretty:
        renderer = structlog.dev.ConsoleRenderer(pad_event=40)
    else:
        renderer = structlog.processors.JSONRenderer(rapidjson.dumps)
        processors.append(structlog.stdlib.render_to_log_kwargs)
    processors.append(renderer)
    return processors


def configure(*processors, level: str):
    """
    Configure `structlog` globally.

    .. _structlog Configuration
        http://www.structlog.org/en/stable/configuration.html
    """
    logging.basicConfig(format='%(message)s', level=level)
    logging.getLogger('asyncio').disabled = True
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def make_proxy(frontend: str, backend: str, proxy_type: int = zmq.FORWARDER,
               frontend_type: int = zmq.SUB, backend_type: int = zmq.PUB) -> zmq.devices.Device:
    proxy = zmq.devices.ThreadDevice(proxy_type, frontend_type, backend_type)
    proxy.bind_in(frontend)
    proxy.bind_out(backend)
    if frontend_type is zmq.SUB:
        proxy.setsockopt_in(zmq.SUBSCRIBE, b'')
    return proxy


def make_log_publisher(frontend_addr: Optional[str] = None) -> zmq.asyncio.Socket:
    context = zmq.asyncio.Context.instance()
    publisher = context.socket(zmq.PUB)
    publisher.connect(frontend_addr or FRONTEND_ADDR)
    return publisher


async def drain_logs(records: asyncio.Queue, publisher: Connection = None):
    config = {'socket_type': zmq.PUB, 'address': FRONTEND_ADDR}
    publisher = publisher or Connection.open(config)
    with publisher:
        while True:
            await publisher.send(await records.get())
