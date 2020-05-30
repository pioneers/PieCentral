import abc
import asyncio
import dataclasses
from numbers import Real
import signal
import threading
import typing

import aiozmq.rpc
import structlog

from runtime import log
from runtime.service.storage import Document


@dataclasses.dataclass
class Service(abc.ABC, aiozmq.rpc.AttrHandler):
    """
    A subprocess that exposes callable methods over RPC.

    Services perform several bookkeeping functions:
      1. Serving RPC requests.
      2. Relaying logs to the log aggregator (forwarder).
      3. Providing access to the central configuration store.
      4. Handling signals.
      5. Monitoring and reporting performance.
    """
    address: str
    config: Document
    debug: bool = False
    logger: typing.Optional[structlog.BoundLoggerBase] = None

    async def main(self):
        """ Service business logic. Can be overriden to perform other tasks. """
        rpc = await aiozmq.rpc.serve_rpc(self, bind=self.address)
        await asyncio.gather(
            rpc.wait_closed(),
            self.broadcast_health(),
            self.logger.relay.forward(),
        )

    def terminate(self):
        self.logger.debug('Terminating service')
        for task in asyncio.all_tasks():
            task.cancel()

    def set_signal_handlers(self):
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, self.terminate)
        loop.add_signal_handler(signal.SIGHUP, self.terminate)

    async def run(self):
        self.set_signal_handlers()
        threading.main_thread().name = f'{self.__class__.__name__.lower()}-main'
        try:
            self.logger = log.get_logger(
                await self.config.get('log.addresses.frontend'),
                pretty = await self.config.get('log.pretty'),
            )
            await self.main()
        except asyncio.CancelledError:
            pass

    async def get_health(self):
        # TODO: add profiler (yappi) stats
        self.logger.info('Service health', threads=threading.active_count())

    async def broadcast_health(self) -> typing.NoReturn:
        """ Profile the subprocess and periodically log performance statistics. """
        interval = await self.config.get('health.interval')
        while True:
            await asyncio.sleep(interval)
            await self.get_health()

    def bootstrap(self):
        """ Process entry point. """
        asyncio.run(self.run(), debug=self.debug)
