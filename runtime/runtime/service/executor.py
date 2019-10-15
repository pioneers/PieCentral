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

    async def set_alliance(self, alliance: Alliance):
        async with self.access:
            self.alliance = alliance

    async def change_mode(self, alliance: Alliance):
        async with self.access:
            pass  # TODO

    async def main(self):
        i = 0
        while i < 5:
            async with self.access:
                self.logger.debug('Sending ping to journal.')
                await self.raw_sockets['journal'].send(b'executor')
            await asyncio.sleep(1)
            i += 1
        from runtime.util.exception import EmergencyStopException
        raise EmergencyStopException()
