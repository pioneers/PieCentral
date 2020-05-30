import asyncio
import collections
import dataclasses
from numbers import Real
import os
import typing
from typing import Any, Callable, Mapping, Optional, TypeVar, Union
from schema import And, Regex, Use


def get_module_path(filename: str) -> str:
    """ Return a path relative to the module's top-level directory. """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, '..', filename)


# Common schema types
VALID_NAME = Regex(r'^[a-zA-Z_]\w*$')
POSITIVE_INTEGER = And(int, lambda n: n > 0)
POSITIVE_REAL = And(Use(float), lambda x: x > 0)

ParameterValue = Union[str, bytes, Real, bool]


@dataclasses.dataclass
class PacketTransportStatistics:
    bytes_recv: int = 0
    bytes_sent: int = 0
    packets_recv: int = 0
    packets_sent: int = 0

    rounding: typing.ClassVar[int] = 3

    def reset(self):
        self.bytes_recv = self.bytes_sent = 0
        self.packets_recv = self.packets_sent = 0

    def record_recv(self, packet_size: int):
        self.bytes_recv += packet_size
        self.packets_recv += 1

    def record_send(self, packet_size: int):
        self.bytes_sent += packet_size
        self.packets_sent += 1

    def as_dict(self) -> dict:
        stats = dataclasses.asdict(self)
        if self.packets_recv:
            stats['mean_bytes_recv'] = round(self.bytes_recv/self.packets_recv, self.rounding)
        if self.packets_sent:
            stats['mean_bytes_sent'] = round(self.bytes_sent/self.packets_sent, self.rounding)
        return stats


class TTLMapping(collections.UserDict):
    """
    An `asyncio`-compatible mapping with expiring entries.

    Every key-value pair is associated with a condition variable that is
    notified when that pair is refreshed, which restarts an expiration timer
    for that pair. When a timer expires, the pair is removed from the mapping
    (and optionally passed to a callback for further cleanup).

    Attributes:
        ttl: The time-to-live of each entry.
        on_expiration: A callback that accepts a key and value as arguments.
            Called when an entry expires. Return value is ignored.
        refreshed: A mapping of keys to condition variables.
    """

    def __init__(self, ttl: Real, on_expiration: Optional[Callable[[Any, Any], None]] = None):
        self.ttl, self.on_expiration, self.refreshed = ttl, on_expiration, {}
        super().__init__()

    async def expire(self, key):
        """ Start an expiration timer, blocking until the entry expires. """
        refreshed = self.refreshed[key]
        try:
            while True:
                async with refreshed:
                    await asyncio.wait_for(refreshed.wait(), self.ttl)
        except asyncio.TimeoutError:
            self.refreshed.pop(key)
            value = self.pop(key)
            if self.on_expiration:
                self.on_expiration(key, value)

    async def keep_alive(self, key):
        """ Refreshes the time-to-live of a key. """
        refreshed = self.refreshed[key]
        async with refreshed:
            refreshed.notify_all()

    def clear(self):
        """ Expire all the keys and remove them from the mapping. """
        for key, value in self.items():
            self.on_expiration(key, value)
        super().clear()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key not in self.refreshed:
            self.refreshed[key] = asyncio.Condition()
