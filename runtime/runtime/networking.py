import asyncio
import functools
import os
import signal
import socket
from typing import Tuple
import msgpack
import aio_msgpack_rpc as rpc

import runtime.journal
from runtime.devices import SensorService
from runtime.store import StoreService
from runtime.util import RuntimeBaseException
from runtime.messaging import make_rpc_server

LOGGER = runtime.journal.make_logger(__name__)

# BUG: `logger.info('call %s%r', name, *args)` does not work with no `args`.
rpc.client.logger.disabled = True
rpc.server.logger.disabled = True

Addr = Tuple[str, int]


class StreamingProtocol(asyncio.DatagramProtocol):
    stat_log_period = 30

    def __init__(self, sensor_server: SensorService):
        self.sensor_server = sensor_server

    def connection_made(self, transport):
        self.transport = transport
        LOGGER.debug('Streaming server connection made.')
        self.bad_msg_count, self.msg_count = 0, 0
        self.stat_log_task = asyncio.ensure_future(self.log_statistics())

    def connection_lost(self, exc):
        LOGGER.debug('Streaming server connection lost.')
        self.stat_log_task.cancel()

    def datagram_received(self, data, addr):
        try:
            command = msgpack.unpackb(data)
        except msgpack.exceptions.ExtraData:
            self.bad_msg_count += 1
        finally:
            self.msg_count += 1

        # TODO

        response = {}
        self.transport.sendto(msgpack.packb(response), addr)

    def error_received(self, exc):
        LOGGER.error(str(exc))

    async def log_statistics(self):
        try:
            while True:
                LOGGER.debug('Streaming server statistics.',
                             bad_msg_count=self.bad_msg_count, msg_count=self.msg_count)
                await asyncio.sleep(self.stat_log_period)
        except asyncio.CancelledError:
            pass

    @classmethod
    async def make_streaming_server(cls, sensor_server, local_addr: Addr, remote_addr: Addr = None):
        return await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: cls(sensor_server),
            local_addr=local_addr,
            remote_addr=remote_addr,
            family=socket.AF_INET,
            reuse_address=True,
            reuse_port=True,
        )


async def start(options):
    try:
        host, rpc_port, stream_recv_port = options['host'], options['tcp'], options['udp_recv']
        rpc_server = await make_rpc_server(StoreService(options), host=host, port=rpc_port)
        sensor_server = await make_rpc_server(SensorService(options['dev_schema']), path=options['net_srv'])
        async with rpc_server, sensor_server:
            LOGGER.info('Starting RPC server.', host=host, port=rpc_port)
            await asyncio.gather(
                rpc_server.serve_forever(),
                sensor_server.serve_forever(),
                StreamingProtocol.make_streaming_server(sensor_server, (host, stream_recv_port)),
            )
    except asyncio.CancelledError:
        if os.path.exists(options['net_srv']):
            os.path.unlink(options['net_srv'])
    finally:
        await rpc_server.wait_closed()
        LOGGER.info('Stopped RPC server gracefully.')
