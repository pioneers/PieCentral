import asyncio

from runtime.service.base import Service


class ExecutorService(Service):
    async def main(self):
        while True:
            self.logger.warning('Hello from the executor!')
            await asyncio.sleep(1)
