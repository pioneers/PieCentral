"""
Low-level networking module for building topologies using ZMQ.

The purpose of this module is to deliver data between endpoints.
"""

import asyncio
import collections
import collections.abc
import dataclasses
import enum
import functools
import math
from typing import List, Mapping, Optional, Union

import msgpack
import structlog
import zmq
import zmq.asyncio

from runtime.util.exception import RuntimeBaseException


if not hasattr(zmq, 'RADIO') or not hasattr(zmq, 'DISH'):
    raise ImportError('Must enable ZMQ draft sockets to use RADIO/DISH')

UDP = set([zmq.RADIO, zmq.DISH])


def make_socket(
        context: zmq.Context,
        socket_type: int,
        address: Union[str, List[str]],
        bind: bool = False,
        group: str = None,
        send_timeout=float('inf'),
        recv_timeout=float('inf')):
    """ Initialize a raw ZMQ socket. """
    socket = context.socket(socket_type)
    if not math.isinf(send_timeout):
        socket.setsockopt(zmq.SNDTIMEO, int(send_timeout))
    if not math.isinf(recv_timeout):
        socket.setsockopt(zmq.RCVTIMEO, int(recv_timeout))

    if bind:
        socket.bind(address)
    else:
        addresses = address if isinstance(address, list) else [address]
        for address in addresses:
            socket.connect(address)

    if socket_type == zmq.SUB:
        socket.subscribe(b'')
    if socket_type == zmq.DISH:
        socket.join(group or b'')
    return socket


@dataclasses.dataclass
class Connection:
    """
    Serializes/deserializes raw binary packets entering/leaving a ZMQ socket.

    References::
        https://pyzmq.readthedocs.io/en/latest/api/zmq.html#zmq.Socket.copy_threshold
    """
    socket: zmq.Socket
    copy: bool = True
    send_group: str = b''
    bytes_sent: int = 0
    bytes_recv: int = 0
    logger: Optional[structlog.BoundLoggerBase] = None

    def __post_init__(self):
        self.udp_send = functools.partial(self.socket.send, copy=self.copy, group=self.send_group)
        self.udp_recv = functools.partial(self.socket.recv, copy=self.copy)

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        self.close()

    def dumps(self, data) -> bytes:
        return msgpack.dumps(data)

    def loads(self, data: bytes):
        return msgpack.loads(data, raw=False)

    @property
    def _is_native_async(self):
        return isinstance(self.socket.context, zmq.asyncio.Context)

    async def send(self, payload):
        """ Serialize the outbound data and send the packet in chunks. """
        packet = self.dumps(payload)
        if self._is_native_async:
            await self.socket.send(packet, copy=self.copy)
        else:
            await asyncio.get_running_loop().run_in_executor(None, self.udp_send, packet)
        self.bytes_sent += len(packet)

    async def recv(self):
        """ Reassemble the incoming packet and deserialize the object. """
        if self._is_native_async:
            packet = await self.socket.recv(copy=self.copy)
        else:
            packet = await asyncio.get_running_loop().run_in_executor(None, self.udp_recv)
        self.bytes_recv += len(packet)
        return self.loads(packet)

    async def req(self, payload):
        if self.socket.type != zmq.REQ:
            raise RuntimeBaseException('Cannot make requests with non-REQ socket')
        await self.send(payload)
        return await self.recv()

    def close(self):
        self.socket.close()
        if self.logger:
            self.logger.debug('Closed connection')

    @staticmethod
    def open(config, context=None, **options):
        context = zmq.asyncio.Context.instance() or context
        socket = make_socket(context, **config)
        connection = Connection(socket, **options)
        if connection.logger:
            connection.logger.debug('Opened connection')
        return connection
