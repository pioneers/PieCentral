"""
Low-level routing module for building networking topologies using ZMQ.

The purpose of this module is to deliver packets of bytes between two endpoints.
"""

import asyncio
import collections
import collections.abc
import dataclasses
import enum
import functools
import math
from typing import List, Mapping, Union

import msgpack
import structlog
import zmq
import zmq.asyncio

from runtime.util.exception import RuntimeBaseException


LOGGER = structlog.get_logger()


class SocketType(enum.IntEnum):
    SUB = zmq.SUB
    PUB = zmq.PUB
    REQ = zmq.REQ
    REP = zmq.REP
    try:
        DISH = zmq.DISH
        RADIO = zmq.RADIO
    except AttributeError:
        raise ImportError('Must enable ZMQ draft sockets to use RADIO/DISH')


UDP = set([SocketType.RADIO, SocketType.DISH])


def make_socket(context: zmq.Context, socket_type: SocketType, address: Union[str, List[str]],
                bind: bool = False, group: str = None, send_timeout=float('inf'),
                recv_timeout=float('inf')):
    """ Initialize a raw ZMQ socket. """
    socket = context.socket(socket_type.value)
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

    if socket_type is SocketType.SUB:
        socket.subscribe(b'')
    if socket_type is SocketType.DISH:
        socket.join(group or b'')
    return socket


def get_socket_type(socket_type: Union[int, str, SocketType]) -> SocketType:
    if isinstance(socket_type, str):
        return SocketType.__members__[socket_type]
    elif isinstance(socket_type, int):
        return SocketType(socket_type)
    else:
        return socket_type


@dataclasses.dataclass
class Connection:
    """
    Serializes/deserializes raw binary packets entering/leaving a ZMQ socket.

    References::
        https://pyzmq.readthedocs.io/en/latest/api/zmq.html#zmq.Socket.copy_threshold
    """
    socket: zmq.Socket
    chunk_size: int = 512
    copy: bool = True
    send_group: str = b''
    bytes_sent: int = 0
    bytes_recv: int = 0

    def __post_init__(self):
        self.udp = SocketType(self.socket.socket_type) in UDP
        self.udp_send = functools.partial(self.socket.send, copy=self.copy, group=self.send_group)
        self.udp_recv = functools.partial(self.socket.recv, copy=self.copy)

    def dumps(self, data) -> bytes:
        return msgpack.dumps(data)

    def loads(self, data: bytes):
        return msgpack.loads(data, raw=False)

    async def send(self, payload):
        """ Serialize the outbound data and send the packet in chunks. """
        packet = self.dumps(payload)
        if self.udp:
            # TODO: no copying
            await asyncio.get_running_loop().run_in_executor(None, self.udp_send, packet)
        else:
            chunks = [packet[i : i+self.chunk_size] for i in range(0, len(packet), self.chunk_size)]
            await self.socket.send_multipart(chunks, copy=self.copy)
        self.bytes_sent += len(packet)

    async def recv(self):
        """ Reassemble the incoming packet and deserialize the object. """
        if self.udp:
            packet = await asyncio.get_running_loop().run_in_executor(None, self.udp_recv)
        else:
            chunks = await self.socket.recv_multipart(copy=self.copy)
            packet = bytearray()  # Modified in place (fast, no-copy).
            for chunk in chunks:
                packet.extend(chunk)
        self.bytes_recv += len(packet)
        return self.loads(packet)

    async def req(self, payload):
        if self.socket.type != SocketType.REQ.value:
            raise RuntimeBaseException('Cannot make requests with non-REQ socket')
        await self.send(payload)
        return await self.recv()

    def close(self):
        self.socket.close()


@dataclasses.dataclass
class ConnectionManager(collections.abc.Mapping):
    udp_context: zmq.Context = dataclasses.field(default_factory=zmq.Context)
    stream_context: zmq.asyncio.Context = dataclasses.field(default_factory=zmq.asyncio.Context)
    connections: Mapping[str, Connection] = dataclasses.field(default_factory=dict)

    def open_connection(self, name: str, socket_config, **conn_options):
        socket_type = get_socket_type(socket_config['socket_type'])
        socket_config['socket_type'] = socket_type
        context = self.udp_context if socket_type in UDP else self.stream_context
        socket = make_socket(context, **socket_config)
        connection = self.connections[name] = Connection(socket, **conn_options)
        socket_config['socket_type'] = socket_type.name
        LOGGER.debug('Created connection', name=name, **socket_config)
        return connection

    def close_connection(self, name: str):
        self.connections.pop(name).close()
        LOGGER.debug('Closed connection', name=name)

    def __enter__(self):
        return self

    def __exit__(self, _type, _exc, _traceback):
        for name in list(self.connections):
            self.close_connection(name)

    def __getattr__(self, name: str):
        return self.connections.get(name)

    def __getitem__(self, name: str):
        return self.connections[name]

    def __iter__(self):
        return iter(self.connections)

    def __len__(self):
        return len(self.connections)
