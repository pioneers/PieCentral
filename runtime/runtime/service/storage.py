import abc
import asyncio
import dataclasses
import functools
import pathlib
import typing

import aiofiles
import aiozmq.rpc
from aiozmq.rpc.rpc import RPCClient
import rapidjson as json
import yaml


class Document(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: typing.Optional[str] = None) -> typing.Any:
        ...

    @abc.abstractmethod
    async def set(self, key: str, value: typing.Any):
        ...

    @abc.abstractmethod
    async def delete(self, key: str):
        ...


@dataclasses.dataclass
class DocumentService(aiozmq.rpc.AttrHandler):
    """
    A nested key-value store backed by persistent storage on disk.
    """
    path: pathlib.Path
    data: typing.Optional[dict] = dataclasses.field(default_factory=dict)
    delimeter: str = '.'
    persisting: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)

    SERIALIZERS = {
        '.yaml': (yaml.safe_load, functools.partial(yaml.safe_dump, default_flow_style=False)),
        '.yml': (yaml.safe_load, functools.partial(yaml.safe_dump, default_flow_style=False)),
        '.json': (json.loads, json.dumps),
    }

    async def load(self, create: bool = True):
        load, _ = self.SERIALIZERS[self.path.suffix]
        if self.path.exists():
            async with aiofiles.open(str(self.path)) as file_handle:
                self.data = load(await file_handle.read())
        else:
            await self.dump()

    async def dump(self):
        _, dump = self.SERIALIZERS[self.path.suffix]
        async with aiofiles.open(str(self.path), 'w+') as file_handle:
            await file_handle.write(dump(self.data))

    def _parse(self, key: str) -> typing.List[str]:
        return key.split(self.delimeter)

    def _traverse(self, *subkeys: str, create: bool = False) -> typing.Any:
        current = self.data
        for subkey in subkeys:
            current = current.setdefault(subkey, {}) if create else current[subkey]
        return current

    @aiozmq.rpc.method
    async def get(self, key: str = None, default=None):
        if key:
            return self._traverse(*self._parse(key))
        return self.data

    @aiozmq.rpc.method
    async def set(self, key: str, value):
        *subkeys, last = self._parse(key)
        self._traverse(*subkeys, create=True)[last] = value
        await self.dump()

    @aiozmq.rpc.method
    async def delete(self, key: str):
        *subkeys, last = self._parse(key)
        del self._traverse(*subkeys)[last]
        await self.dump()


@dataclasses.dataclass
class DocumentClient(Document):
    address: str
    namespace: typing.Optional[str] = None
    client: typing.Optional[RPCClient] = None

    async def _get_client(self):
        if not self.client:
            self.client = await aiozmq.rpc.connect_rpc(connect=self.address)
            self.client = self.client.call
            if self.namespace:
                for name in self.namespace.split('.'):
                    self.client = getattr(self.client, name)
        return self.client

    async def get(self, *args, **kwargs):
        client = await self._get_client()
        return await client.get(*args, **kwargs)

    async def set(self, *args, **kwargs):
        client = await self._get_client()
        return await client.set(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        client = await self._get_client()
        return await client.delete(*args, **kwargs)
