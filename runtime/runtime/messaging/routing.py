"""
Low-level routing module for building networking topologies using ZMQ.

The purpose of this module is to deliver packets of bytes to various agents.
"""

import collections
import dataclasses
import functools
import enum
from typing import Callable, Set, Tuple

import backoff
import msgpack
import structlog
import zmq
from zmq.asyncio import Context, Socket

from runtime.monitoring.retry import Proxy, Policies


def make_socket(context: Context, socket_type: int, address: str,
                send_timeout: int = 5000, recv_timeout: int = 5000):
    """ Initialize a raw ZMQ socket. """
    socket = context.socket(socket_type)
    socket.setsockopt(zmq.SNDTIMEO, send_timeout)
    socket.setsockopt(zmq.RCVTIMEO, recv_timeout)

    if socket_type in (zmq.PUB, zmq.REP, zmq.PUSH):
        socket.bind(address)
    else:
        socket.connect(address)
    if socket_type == zmq.SUB:
        socket.subscribe(b'')
    return socket


def make_retryable_socket(socket_factory: Callable, logger, policies: Policies = None):
    """
    References::
        * http://zguide.zeromq.org/py:lpclient
    """
    if policies is None:
        default_policy = functools.partial(
            backoff.on_exception,
            backoff.constant,
            zmq.ZMQError,
            max_tries=10,
        )
        policies = collections.defaultdict(lambda: default_policy)
    return Proxy(socket_factory, logger, policies, lambda socket: socket.close(linger=0))


@dataclasses.dataclass
class Connection:
    """ Serializes/deserializes raw binary packets entering/leaving a ZMQ socket. """
    socket: Socket
    chunk_size: int = 512

    def dumps(self, data) -> bytes:
        return msgpack.dumps(data)

    def loads(self, data: bytes):
        return msgpack.loads(data)

    async def send(self, data):
        """ Serialize the outbound data and send the packet in chunks. """
        packet = self.dumps(data)
        chunks = [packet[i : i+self.chunk_size] for i in range(0, len(packet), self.chunk_size)]
        await self.socket.send_multipart(chunks, copy=False)

    async def recv(self):
        """ Reassemble the incoming packet and deserialize the object. """
        chunks = await self.socket.recv_multipart(copy=False)
        packet = bytearray()  # Modified in place (fast, no-copy).
        for chunk in chunks:
            packet.extend(chunk)
        return self.loads(packet)
