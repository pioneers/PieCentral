"""
Low-level routing module for building networking topologies using ZMQ.

The purpose of this module is to deliver packets of bytes between two endpoints.
"""

import dataclasses
import math

import msgpack
import zmq
from zmq.asyncio import Context, Socket


SOCKET_TYPES = {
    'SUB': zmq.SUB,
    'PUB': zmq.PUB,
}


def make_socket(context: Context, socket_type: int, address: str, bind=False,
                send_timeout=float('inf'), recv_timeout=float('inf')):
    """ Initialize a raw ZMQ socket. """
    socket = context.socket(socket_type)
    if not math.isinf(send_timeout):
        socket.setsockopt(zmq.SNDTIMEO, int(send_timeout))
    if not math.isinf(recv_timeout):
        socket.setsockopt(zmq.RCVTIMEO, int(recv_timeout))

    if bind:
        socket.bind(address)
    else:
        socket.connect(address)
    if socket_type == zmq.SUB:
        socket.subscribe(b'')
    return socket


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
