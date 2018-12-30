import asyncio
import functools
import aio_msgpack_rpc as rpc
from runtime.util import RuntimeBaseException


async def make_rpc_server(service, host=None, port=None, path=None, server_options: dict = None, **transport_options):
    server_options = server_options or {}
    server = rpc.Server(service, **server_options)
    if host and port:
        return await asyncio.start_server(server, host=host, port=port, **transport_options)
    elif path:
        return await asyncio.start_unix_server(server, path=path, **transport_options)
    else:
        raise RuntimeBaseException('Must run service with TCP or UNIX sockets.')


async def make_rpc_client(host=None, port=None, path=None, client_options: dict = None, **transport_options):
    client_options = client_options or {}
    if host and port:
        reader, writer = await asyncio.open_connection(host, port, **transport_options)
    elif path:
        reader, writer = await asyncio.open_unix_connection(path, **transport_options)
    else:
        raise RuntimeBaseException('Must connect to service with TCP or UNIX sockets.')
    return rpc.Client(reader, writer, **client_options)


class Circuitbreaker:
    transient_errors = (
        asyncio.IncompleteReadError,
        asyncio.LimitOverrunError,
        ConnectionResetError,
        ConnectionRefusedError,
        FileNotFoundError,
    )

    def __init__(self, retry_cooldown=3, logger=None, **client_options):
        self.retry_cooldown, self.logger = retry_cooldown, logger
        self.client_options = client_options
        self._get_method_wrapper = functools.lru_cache(maxsize=1024)(self._get_method_wrapper)

    async def _get_client(self):
        if 'client' not in self.__dict__:
            self.__dict__['client'] = await make_rpc_client(**self.client_options)
        return self.__dict__['client']

    def _get_method_wrapper(self, name):
        fail_count = 0  # Local to each method
        async def method_wrapper(*args, block=True, **kwargs):
            nonlocal fail_count
            while True:
                try:
                    client = await self._get_client()
                    if block:
                        return await client.call(name, *args, **kwargs)
                    else:
                        return client.notify(name, *args, **kwargs)
                except self.transient_errors as exc:
                    fail_count += 1
                    if self.logger:
                        self.logger.warning(
                            f'Transient error. Retrying.',
                            fail_count=fail_count,
                            exc_name=exc.__class__.__name__,
                        )
                else:
                    fail_count = 0
                await asyncio.sleep(self.retry_cooldown)
        method_wrapper.__name__ = name
        return method_wrapper

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return self._get_method_wrapper(name)
