import asyncio
from concurrent.futures import ThreadPoolExecutor
import ctypes
import dataclasses
from numbers import Real
from typing import Mapping

from schema import Optional
import structlog
import zmq
import zmq.asyncio

from runtime.service.base import Service
from runtime.messaging.device import (
    DeviceBuffer,
    DeviceMapping,
    SmartSensorStructure,
    get_device_type,
)
from runtime.messaging.routing import Connection, ConnectionManager
from runtime.util import POSITIVE_INTEGER, POSITIVE_REAL, VALID_NAME, TTLMapping
from runtime.util.exception import RuntimeBaseException


LOGGER = structlog.get_logger()


@dataclasses.dataclass
class DatagramServer:
    connections: ConnectionManager
    config: dict
    device_buffers: DeviceMapping = dataclasses.field(init=False, default=None)
    clients: TTLMapping = dataclasses.field(default=None, init=False)
    send_count: int = 0
    recv_count: int = 0

    def __post_init__(self):
        self.device_buffers = DeviceMapping(self.config['device_timeout'], LOGGER)
        self.clients = TTLMapping(self.config['client_timeout'], self.on_client_disconnect)

    def __enter__(self):
        return self

    def __exit__(self, _type, _exc, _traceback):
        self.device_buffers.clear()

    async def handle_client(self, address: str):
        """
        Create or keep alive a connection for a new client.
        """
        if address in self.clients:
            await self.clients.keep_alive(address)
        else:
            socket_config = {'socket_type': 'RADIO', 'address': address}
            self.clients[address] = self.connections.open_connection(address, socket_config)
            asyncio.create_task(self.clients.expire(address))
            LOGGER.debug('New datagram client connected', address=address)

    def on_client_disconnect(self, address: str, _connection: Connection):
        self.connections.close_connection(address)
        LOGGER.debug('Client disconnected', address=address)

    async def update_gamepad_data(self, gamepad_id: int, gamepad_data):
        device_uid = f'gamepad-{gamepad_id}'
        device_type = get_device_type(protocol='dawn', device_name='Gamepad')
        await self.device_buffers.open(device_uid, device_type, create=True)
        struct = self.device_buffers[device_uid].struct
        struct.set_current('joystick_left_x', gamepad_data.get('lx', 0))
        struct.set_current('joystick_left_y', gamepad_data.get('ly', 0))
        struct.set_current('joystick_right_x', gamepad_data.get('rx', 0))
        struct.set_current('joystick_right_y', gamepad_data.get('ry', 0))
        button_map = gamepad_data.get('btn', 0)
        gamepad_type = get_device_type(protocol='dawn', device_name='Gamepad')
        for i, param in enumerate(gamepad_type._params):
            if param.type == ctypes.c_bool:
                struct.set_current(param.name, bool((button_map >> i) & 0b1))

    async def recv_loop(self):
        while True:
            message = await self.connections.datagram_recv.recv()
            self.recv_count += 1
            try:
                address = message.get('src')
                if address:
                    await self.handle_client(address)
                gamepads = message.get('gamepads') or {}
                for gamepad_id, gamepad in gamepads.items():
                    if 0 <= gamepad_id < self.config['max_gamepads']:
                        await self.update_gamepad_data(gamepad_id, gamepad)
                    else:
                        LOGGER.warn('Invalid gamepad ID', gamepad_id=gamepad_id,
                                    max_gamepads=self.config['max_gamepads'])
            except RuntimeBaseException as exc:
                LOGGER.warn('Encountered error while decoding datagram', exc=str(exc))

    async def broadcast(self):
        device_updates = {}
        for device in self.device_buffers.values():
            if device.is_smart_sensor:
                device_update = device_updates[str(device.struct.uid.to_int())] = {}
                device_update['type'] = type(device.struct).__name__
                device_update['params'] = params = {}

                # device.struct.set_current('tag_detect', 1) # TODO: remove after testing

                for param in device.struct.get_parameters(device.struct.send):
                    params[param.name] = device.struct.get_current(param.name)
                device.struct.send = SmartSensorStructure.RESET_MAP

        update = {'devices': device_updates}
        for client in self.clients.values():
            asyncio.create_task(client.send(update))
            self.send_count += 1

    async def log_statistics(self):
        while True:
            await asyncio.sleep(self.config['log_interval'])
            bytes_sent = 0
            for client in self.clients.values():
                bytes_sent += client.bytes_sent
                client.bytes_sent = 0
            recv_conn = self.connections.datagram_recv
            LOGGER.info(
                'Datagram server statistics', clients=list(self.clients),
                send_count=self.send_count, recv_count=self.recv_count,
                bytes_sent=bytes_sent, bytes_recv=recv_conn.bytes_recv,
            )
            self.send_count, self.recv_count, recv_conn.bytes_recv = 0, 0, 0

    async def send_loop(self):
        loop = asyncio.get_running_loop()
        start, interval = loop.time(), self.config['sensor_send_interval']
        while True:
            try:
                start = loop.time()
                await asyncio.wait_for(self.broadcast(), interval)
                duration = loop.time() - start
                time_remaining = interval - duration
                if time_remaining > 0:
                    await asyncio.sleep(time_remaining)
            except asyncio.TimeoutError:
                LOGGER.warn('Send cycle timed out')

    async def listen_for_device_status(self):
        while True:
            status = await self.connections.sensor_status.recv()
            devices = status.get('devices') or []
            for device in devices:
                device_type = get_device_type(device_name=device['device_type'])
                await self.device_buffers.open(device['device_uid'], device_type)

    async def broadcast_status(self):
        while True:
            devices = [buffer.status for buffer in self.device_buffers.values()
                       if not buffer.is_smart_sensor]
            await self.connections.gamepad_status.send({'devices': devices})
            await asyncio.sleep(self.config['gamepad_send_interval'])


@dataclasses.dataclass
class BrokerService(Service):
    config_schema = {
        **Service.config_schema,
        Optional('max_workers', default=5): POSITIVE_INTEGER,
        Optional('sensor_send_interval', default=0.1): POSITIVE_REAL,
        Optional('log_interval', default=30): POSITIVE_REAL,
        Optional('device_timeout', default=1): POSITIVE_REAL,
        Optional('client_timeout', default=15): POSITIVE_REAL,
        Optional('gamepad_send_interval', default=0.5): POSITIVE_REAL,
        Optional('max_gamepads', default=4): POSITIVE_INTEGER,
        Optional('proxies', default={}): {
            VALID_NAME: {
                'frontend': VALID_NAME,
                'backend': VALID_NAME,
            }
        },
    }

    def serve_proxy(self, proxy):
        frontend, backend = proxy['frontend'], proxy['backend']
        frontend_socket = self.connections[frontend].socket
        backend_socket = self.connections[backend].socket
        LOGGER.debug('Serving proxy', frontend=frontend, backend=backend)
        # `zmq.proxy` is a C extension function, which `pylint` cannot detect.
        # pylint: disable=no-member
        zmq.proxy(frontend_socket, backend_socket)  # FIXME

    async def serve_proxies(self):
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as thread_pool:
            loop = asyncio.get_running_loop()
            proxies = [loop.run_in_executor(thread_pool, self.serve_proxy, proxy)
                       for proxy in self.config['proxies'].values()]
            await asyncio.wait(proxies)

    async def main(self):
        with DatagramServer(self.connections, self.config) as datagram_server:
            await asyncio.gather(
                self.serve_proxies(),
                datagram_server.recv_loop(),
                datagram_server.send_loop(),
                datagram_server.log_statistics(),
                datagram_server.broadcast_status(),
                datagram_server.listen_for_device_status(),
            )
