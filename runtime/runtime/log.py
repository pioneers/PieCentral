import asyncio
import dataclasses
import logging
import threading
import typing
from typing import Optional, Tuple

import aiozmq.rpc
import msgpack
import rapidjson
import structlog
import structlog.processors
import structlog.stdlib
import zmq
import zmq.devices

from runtime.service.storage import Document


@dataclasses.dataclass
class LogRelay:
    """
    A ``structlog`` processor that forwards records to a log aggregator.

    Internally, the relay is attached to an asyncio loop by ``forward``. The
    ``forward`` coroutine will forever consume log events stored in an internal
    queue and publish them to the aggregator, the frontend of a ZMQ device.

    Once a loop is attached, events can be safely enqueued from any thread. Log
    events are not enqueued while a loop is not attached.

    References::
        .. _http://www.structlog.org/en/stable/processors.html
    """
    frontend: str
    loop: typing.Optional[asyncio.AbstractEventLoop] = None
    buffer: typing.Optional[asyncio.Queue] = None

    @property
    def ready(self) -> bool:
        """ True if an asyncio loop is attached and the buffer is initialized. """
        return bool(self.loop and self.buffer)

    def __call__(self, _logger, method: str, event: dict):
        """ Ingest a log event. """
        if self.ready:
            enqueue = self.buffer.put((method, event.copy()))
            try:
                if self.loop is asyncio.get_running_loop():
                    asyncio.create_task(enqueue, name='log-enqueue')
                else:
                    raise RuntimeError
            except RuntimeError:
                asyncio.run_coroutine_threadsafe(enqueue, self.loop)
        return event

    async def forward(self):
        """ Forward log events to the aggregator, using method names as the topics. """
        if not self.ready:
            self.loop, self.buffer = asyncio.get_running_loop(), asyncio.Queue()
        publisher = await aiozmq.rpc.connect_pubsub(connect=self.frontend)
        try:
            while True:
                method, event = await self.buffer.get()
                self.buffer.task_done()
                await publisher.publish(method).log(event)
        finally:
            publisher.close()


def get_logger(frontend: str, *args, pretty: bool = True, **kwargs):
    """ Return a structlog instance with a log relay. """
    relay = LogRelay(frontend)
    processors = get_processors(relay, pretty=pretty)
    logger = structlog.get_logger(*args, processors=processors, **kwargs)
    logger.relay = relay
    return logger


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
        *extra_processors,
    ]

    if pretty:
        renderer = structlog.dev.ConsoleRenderer(pad_event=40)
    else:
        renderer = structlog.processors.JSONRenderer(rapidjson.dumps)
    processors.append(renderer)
    return processors


def configure(level: str, *processors):
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


def make_proxy(frontend: str, backend: str) -> zmq.devices.Device:
    proxy = zmq.devices.ThreadDevice(zmq.FORWARDER, zmq.SUB, zmq.PUB)
    proxy.bind_in(frontend)
    proxy.bind_out(backend)
    proxy.setsockopt_in(zmq.SUBSCRIBE, b'')
    return proxy


async def start_log_proxy(config: Document):
    processors = get_processors(pretty = await config.get('log.pretty'))
    configure(await config.get('log.level'), *processors)
    proxy = make_proxy(
        await config.get('log.addresses.frontend'),
        await config.get('log.addresses.backend'),
    )
    proxy.start()
