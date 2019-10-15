import asyncio
import enum
import dataclasses

from runtime.service.base import Service


class Mode(enum.IntEnum):
    IDLE = enum.auto()
    AUTO = enum.auto()
    TELEOP = enum.auto()


class Alliance(enum.IntEnum):
    BLUE = enum.auto()
    GOLD = enum.auto()


@dataclasses.dataclass
class ExecutorService(Service):
    access: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    alliance: Alliance = None
    mode: Mode = None

    async def set_alliance(self, alliance: Alliance = None):
        async with self.access:
            self.alliance = alliance

    async def change_mode(self, mode: Mode = None):
        async with self.access:
            pass  # TODO

    async def main(self, config):
        while True:
            self.logger.info('Executor firing')
            await asyncio.sleep(1)
