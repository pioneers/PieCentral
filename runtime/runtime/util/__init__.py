import asyncio
import collections
import dataclasses
from numbers import Real
import os
from schema import And, Regex, Use
from typing import Any, Callable, Mapping, Optional, TypeVar


def get_module_path(filename: str) -> str:
    """ Return a path relative to the module's top-level directory. """
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, '..', filename)


# Common schema types
VALID_NAME = Regex(r'^[a-zA-Z_]\w*$')
POSITIVE_INTEGER = And(int, lambda n: n > 0)
POSITIVE_REAL = And(Use(float), lambda x: x > 0)


class TTLMapping(collections.UserDict):
    def __init__(self, ttl: Real, on_expiration: Optional[Callable[[Any], None]] = None):
        self.ttl, self.on_expiration, self.refreshed = ttl, on_expiration, {}
        super().__init__()

    async def expire(self, key):
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
        refreshed = self.refreshed[key]
        async with refreshed:
            refreshed.notify_all()

    def clear(self):
        for key, value in self.items():
            self.on_expiration(key, value)
        super().clear()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key not in self.refreshed:
            self.refreshed[key] = asyncio.Condition()
