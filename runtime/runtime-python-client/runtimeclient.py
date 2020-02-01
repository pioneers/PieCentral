"""
runtimeclient -- Runtime teleoperation and control
"""

import asyncio
import collections
import dataclasses
import queue
from typing import Mapping

import msgpack
import structlog
import zmq
if not hasattr(zmq, 'RADIO') or not hasattr(zmq, 'DISH'):
    # RADIO/DISH (i.e. UDP) sockets are still not stable APIs, so we must
    # obtain a prerelease version of `zmq`.
    raise ImportError('Must install ZMQ with draft sockets '
                      '(https://pyzmq.readthedocs.io/en/latest/draft.html)')
import zmq.asyncio


class RuntimeClientError(Exception):
    """ Base class for all Runtime errors. """


Gamepad = collections.namedtuple('Gamepad', [
    'button_a',
    'button_b',
    'button_x',
    'button_y',
    'l_bumper',
    'r_bumper',
    'l_trigger',
    'r_trigger',
    'button_back',
    'button_start',
    'l_stick',
    'r_stick',
    'dpad_up',
    'dpad_down',
    'dpad_left',
    'dpad_right',
    'button_xbox',
    'joystick_left_x',
    'joystick_left_y',
    'joystick_right_x',
    'joystick_right_y',
], defaults=([False]*17 + [0]*4))


@dataclasses.dataclass
class RuntimeClient:
    """
    A Runtime client representing a connection to a single robot.

    Communication with Runtime occurs over ZeroMQ sockets `ZMQ`_:
        1. datagram_send: Sends gamepad parameters to Runtime using UDP, an
            unreliable transport.
        2. datagram_recv: Receives sensor and execution data from Runtime over UDP.
        3. command: Issues command synchronously (i.e., request/response) over TCP.
        4. log: Subscribes to asynchronous notifications over TCP from
            Runtime or student code print statements.

    .. _ZMQ:
        https://zeromq.org/
    """
    host: str
    socket_config: dict = dataclasses.field(default_factory=lambda: {
        'datagram_send': ('udp', 6000, zmq.RADIO),
        'datagram_recv': ('udp', 6001, zmq.DISH),
        'command': ('tcp', 6002, zmq.REQ),
        'log': ('tcp', 6003, zmq.SUB),
    })
    logger: structlog.BoundLoggerBase = dataclasses.field(default_factory=structlog.get_logger)
    sockets: Mapping[str, zmq.Socket] = dataclasses.field(default_factory=dict)
    context: zmq.Context = dataclasses.field(default_factory=zmq.Context)
    bytes_sent: int = 0
    bytes_recv: int = 0
    message_id: int = 0
    copy: bool = True

    request, response = 0, 1

    def __enter__(self):
        self.connect_all()
        return self

    def __exit__(self, _type, _exc, _traceback):
        for name in list(self.sockets):
            self.close(name)

    def _get_address(self, protocol: str, port: int) -> str:
        return '{0}://{1}:{2}'.format(protocol, self.host, port)

    def _send(self, name: str, payload):
        packet = msgpack.dumps(payload)
        self.bytes_sent += len(packet)
        return self.sockets[name].send(packet)

    def _recv(self, name: str):
        packet = self.sockets[name].recv()
        self.bytes_recv += len(packet)
        return msgpack.loads(packet, raw=False)

    def connect(self, name: str, protocol: str, port: int, socket_type: int):
        """ Connect a socket. """
        socket = self.sockets[name] = self.context.socket(socket_type)
        address = self._get_address(protocol, port)
        if socket_type != zmq.DISH:
            socket.connect(address)
        else:
            socket.bind(address)
        if socket_type == zmq.SUB:
            socket.subscribe(b'')
        if socket_type == zmq.DISH:
            socket.join(b'')
        self.logger.debug('Connected socket', name=name, address=address, socket_type=socket_type)

    def connect_all(self):
        for name, config in self.socket_config.items():
            self.connect(name, *config)

    def send_datagram(self, gamepads: Mapping[int, Gamepad] = None, ip_addr: str = None):
        """ Send a datagram with Gamepad data. """
        gamepad_data = {}
        for index, gamepad in gamepads.items():
            gamepad_data[index] = {
                'lx': gamepad.joystick_left_x,
                'ly': gamepad.joystick_left_y,
                'rx': gamepad.joystick_right_x,
                'ry': gamepad.joystick_right_y,
                'btn': 0x00000,
            }
            button_map = 0x00000
            for offset in range(17):
                if gamepad[offset]:
                    button_map |= (1 << offset)
            gamepad_data[index]['btn'] = button_map

        payload = {'gamepads': gamepad_data}
        if ip_addr:
            protocol, port, _ = self.socket_config['datagram_recv']
            payload['src'] = self._get_address(protocol, port)
        return self._send('datagram_send', payload)

    def recv_datagram(self):
        """ Receive a datagram with sensor and execution data. """
        return self._recv('datagram_recv')

    def send_command(self, command_name: str, *args):
        """
        Send a command to Runtime and return the result.

        Raises::
            RuntimeClientError: When the command cannot be completed successfully.
        """
        message_id = self.message_id = (self.message_id + 1)%2**32
        try:
            self._send('command', [self.request, message_id, command_name, args])
            message_type, res_message_id, error, result = self._recv('command')
            if message_type != self.response:
                raise RuntimeClientError('Received malformed response')
            if res_message_id != message_id:
                raise RuntimeClientError(
                    'Response message ID did not match '
                    '(expected: {0}, actual: {1})'.format(message_id, res_message_id)
                )
            if error:
                raise RuntimeClientError('Received error from server: {0}'.format(error))
        except (ValueError, msgpack.UnpackException) as exc:
            self.logger.error(str(exc))
            raise RuntimeClientError('Unable to execute command') from exc
        else:
            self.logger.debug('Executed command', command=command_name, message_id=message_id)
            return result

    def recv_log(self):
        """ Read the next entry in the log. """
        return self._recv('log')

    def reset_counters(self):
        """ Reset the client's statistics, including bytes sent/received. """
        self.bytes_sent = self.bytes_recv = 0

    def close(self, name: str):
        """ Close a named socket. """
        self.sockets.pop(name).close()
        self.logger.debug('Closed socket', name=name)
