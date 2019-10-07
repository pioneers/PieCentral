import abc
import asyncio
import dataclasses
import datetime

import structlog


@dataclasses.dataclass
class Service(abc.ABC):
    logger: structlog.BoundLoggerBase = dataclasses.field(default_factory=structlog.get_logger)
    shutdown_timeout: datetime.timedelta = datetime.timedelta(seconds=10)

    def __call__(self):
        asyncio.run(self.bootstrap())

    async def bootstrap(self):
        await self.main()

    @abc.abstractmethod
    async def main(self):
        pass
