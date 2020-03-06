"""
Low-level networking module for building topologies using ZMQ.

The purpose of this module is to deliver data between endpoints.
"""

import asyncio
import collections
import dataclasses
import functools
import math
from typing import Callable, List, Optional, Union

import msgpack
import structlog
import zmq
import zmq.asyncio

from runtime.util.exception import RuntimeBaseException


if not hasattr(zmq, 'RADIO') or not hasattr(zmq, 'DISH'):
    raise ImportError('Must enable ZMQ draft sockets to use RADIO/DISH')

UDP = set([zmq.RADIO, zmq.DISH])  # pylint: disable=no-member


def make_socket(
        context: zmq.Context,
        socket_type: int,
        address: Union[str, List[str]],
        bind: bool = False,
        group: str = None,
        send_timeout=float('inf'),
        recv_timeout=float('inf')):
    """
    Make a raw ZMQ socket.

    Arguments:
        context: The ZMQ context.
        socket_type: A constant
    """
    socket = context.socket(socket_type)
    if not math.isinf(send_timeout):
        socket.setsockopt(zmq.SNDTIMEO, int(send_timeout))
    if not math.isinf(recv_timeout):
        socket.setsockopt(zmq.RCVTIMEO, int(recv_timeout))

    if bind:
        socket.bind(address)
    else:
        addresses = address if isinstance(address, list) else [address]
        for addr in addresses:
            socket.connect(addr)

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
    udp_send: Optional[Callable] = None
    udp_recv: Optional[Callable] = None

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

    @classmethod
    def open(cls, config, context=None, **options):
        context = zmq.asyncio.Context.instance() or context
        socket = make_socket(context, **config)
        connection = cls(socket, **options)
        if connection.logger:
            connection.logger.debug('Opened connection')
        return connection


@dataclasses.dataclass
class RPCConnection(Connection):
    message_id: int = 0

    REQUEST, RESPONSE, NOTIFICATION = 0, 1, 2

    async def _respond_rpc(self, response, context):
        try:
            await self.send(response)
        except OverflowError as exc:
            response[3] = None
            await self.send(response)
            raise RuntimeBaseException('Encountered overflow while serializing response',
                                       **context) from exc
        finally:
            if self.logger:
                self.logger.debug('Sent response', **context)

    async def _handle_rpc_call(self, dispatch):
        try:
            message_type, message_id, method, params = await self.recv()
        except (TypeError, ValueError) as exc:
            raise RuntimeBaseException('Malformed RPC request') from exc
        context = {'message_id': message_id, 'method': method}
        if message_type != RPCConnection.REQUEST:
            raise RuntimeBaseException('Malformed RPC request (not a request)', **context)
        if self.logger:
            self.logger.debug('Received request', **context)

        response = [RPCConnection.RESPONSE, message_id, None, None]
        try:
            response[3] = await dispatch(method, *params)
        except Exception as exc:
            response[2] = str(exc)
            raise RuntimeBaseException('Unable to execute command', **context) from exc
        finally:
            await self._respond_rpc(response, context)

    async def dispatch_loop(self, dispatch, sync=True):
        handle = self._handle_rpc_call if sync else self._handle_rpc_notification
        while True:
            try:
                await handle(dispatch)
            except RuntimeBaseException as exc:
                if self.logger:
                    self.logger.error(str(exc), exc_info=exc, **exc.context)

    async def call(self, method, *params, message_id: Optional[int] = None):
        if message_id is None:
            message_id = self.message_id
            self.message_id += 1
        response = await self.req([RPCConnection.REQUEST, message_id, method, params])
        message_type, res_msg_id, error, result = response
        if message_type != RPCConnection.RESPONSE:
            raise RuntimeBaseException('RPC response has bad type')
        if message_id != res_msg_id:
            raise RuntimeBaseException('RPC message IDs do not match',
                                       req_msg_id=message_id, res_msg_id=res_msg_id)
        if error:
            raise RuntimeBaseException('RPC returned an error', err=str(error))
        return result

    async def _handle_rpc_notification(self, dispatch):
        try:
            message_type, method, params = await self.recv()
        except (TypeError, ValueError) as exc:
            raise RuntimeBaseException('Malformed RPC notification') from exc
        if message_type != RPCConnection.NOTIFICATION:
            raise RuntimeBaseException('Malformed RPC request (not a notification)', method=method)
        # FIXME: too verbose
        # if self.logger:
        #     self.logger.debug('Received notification', method=method)
        asyncio.create_task(dispatch(method, *params))

    async def notify(self, method, *params):
        await self.send([RPCConnection.NOTIFICATION, method, params])