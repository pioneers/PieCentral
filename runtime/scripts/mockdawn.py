#!/usr/bin/env python3

"""
mockdawn -- A command-line tool to send commands to Dawn without gamepads.
"""

import asyncio
import click
import curses
import dataclasses
import functools
import math
import threading

import msgpack
import zmq


@dataclasses.dataclass
class RuntimeClient:
    ...
    # address: str
    # context: zmq.Context = dataclasses.field(default_factory=zmq.Context)
    # socket: zmq.Socket = dataclasses.field(init=False, default=None)
    #
    # def __post_init__(self):
    #     pass
    #
    # def dumps(self, data) -> bytes:
    #     return msgpack.dumps(data)
    #
    # def loads(self, data: bytes):
    #     return msgpack.loads(data, raw=False)


@dataclasses.dataclass
class Gamepad:
    a: bool = False
    b: bool = False
    x: bool = False
    y: bool = False
    left_bumper: bool = False
    right_bumper: bool = False
    left_trigger: bool = False
    right_trigger: bool = False
    back: bool = False
    start: bool = False
    left_stick: bool = False
    right_stick: bool = False
    dpad_up: bool = False
    dpad_down: bool = False
    dpad_left: bool = False
    dpad_right: bool = False
    xbox: bool = False
    joystick_left_x: float = 0
    joystick_left_y: float = 0
    joystick_right_x: float = 0
    joystick_right_y: float = 0

    BUTTON_ACTIVE: int = 1
    BUTTON_MAP = {
        'i': 'dpad_up',
        'j': 'dpad_left',
        'k': 'dpad_down',
        'l': 'dpad_right',
        'r': 'left_bumper',
        'y': 'right_bumper',
        'u': 'left_trigger',
        'o': 'right_trigger',
        'b': 'back',
        'n': 'start',
        't': 'y',
        'f': 'x',
        'g': 'a',
        'h': 'b',
        'x': 'xbox',
        'm': 'right_stick',
        'z': 'left_stick',
    }
    JOYSTICK_DELTA = 0.1

    def update_joystick(self, key, left, right, up, down, side: str = 'left'):
        x, y = getattr(self, f'joystick_{side}_x'), getattr(self, f'joystick_{side}_y')
        if key == left:
            x = max(-1, x - self.JOYSTICK_DELTA)
        elif key == right:
            x = min(1, x + self.JOYSTICK_DELTA)
        elif key == up:
            y = min(1, y + self.JOYSTICK_DELTA)
        elif key == down:
            y = max(-1, y - self.JOYSTICK_DELTA)
        if x**2 + y**2 <= 1:
            setattr(self, f'joystick_{side}_x', x)
            setattr(self, f'joystick_{side}_y', y)

    def update(self, key: str):
        try:
            button = self.BUTTON_MAP[key]
            setattr(self, button, not getattr(self, button))
        except KeyError:
            pass
        self.update_joystick(key, 'a', 'd', 'w', 's')
        self.update_joystick(key, 'KEY_LEFT', 'KEY_RIGHT', 'KEY_UP', 'KEY_DOWN', 'right')

    def as_dict(self):
        payload = {}
        for name, field in self.__class__.__dataclass_fields__.items():
            if field.type is bool and getattr(self, name):
                payload[name] = True
        return payload


def draw_circle(screen, center, y_axis_half_len: int, x_axis_half_len: int,
                samples=100, ch='.'):
    center_y, center_x = center
    dtheta = 2*math.pi/samples
    for i in range(0, samples):
        theta = i*dtheta
        y = center_y - y_axis_half_len*math.sin(theta)
        x = center_x + x_axis_half_len*math.cos(theta)
        screen.addch(int(round(y)), int(round(x)), ch)


def draw_gamepad(screen, gamepad: Gamepad, top: int = 5, left: int = 2):
    active = curses.color_pair(Gamepad.BUTTON_ACTIVE) | curses.A_BOLD
    color_of = lambda attr: active if getattr(gamepad, attr) else 0

    screen.addch(top, left + 2, '^', color_of('dpad_up'))
    screen.addch(top + 1, left, '<', color_of('dpad_left'))
    screen.addch(top + 1, left + 4, '>', color_of('dpad_right'))
    screen.addch(top + 2, left + 2, 'v', color_of('dpad_down'))
    screen.addstr(top + 4, left, 'D-Pad')
    screen.addstr(top + 5, left, '(IJKL)')

    screen.addstr(top, left + 11, 'Y', color_of('y'))
    screen.addstr(top + 1, left + 9, 'X', color_of('x'))
    screen.addstr(top + 1, left + 13, 'B', color_of('b'))
    screen.addstr(top + 2, left + 11, 'A', color_of('a'))
    screen.addstr(top + 4, left + 9, 'Buttons')
    screen.addstr(top + 5, left + 9, '(TFGH)')

    screen.addstr(top, left + 19, 'LB (R)', color_of('left_bumper'))
    screen.addstr(top, left + 28, 'RB (Y)', color_of('right_bumper'))
    screen.addstr(top + 2, left + 19, 'LT (U)', color_of('left_trigger'))
    screen.addstr(top + 2, left + 28, 'RT (O)', color_of('right_trigger'))

    screen.addstr(top + 4, left + 19, '(B)ACK', color_of('back'))
    screen.addstr(top + 4, left + 28, '(X)BOX', color_of('xbox'))
    screen.addstr(top + 4, left + 37, 'START (N)', color_of('start'))

    left_center = (top + 13, left + 12)
    draw_circle(screen, left_center, 6, 12)
    left_y = left_center[0] - 6*gamepad.joystick_left_y
    left_x = left_center[1] + 12*gamepad.joystick_left_x
    screen.addch(int(round(left_y)), int(round(left_x)), '@', active)
    screen.addch(*left_center, 'Z', color_of('left_stick'))
    screen.addstr(top + 21, left, 'Left Joystick (WASD)')

    right_center = (top + 13, left + 40)
    draw_circle(screen, right_center, 6, 12)
    left_y = right_center[0] - 6*gamepad.joystick_right_y
    left_x = right_center[1] + 12*gamepad.joystick_right_x
    screen.addch(int(round(left_y)), int(round(left_x)), '@', active)
    screen.addch(*right_center, 'M', color_of('right_stick'))
    screen.addstr(top + 21, left + 28, 'Right Joystick (Arrows)')


async def send_datagrams(gamepad, client, group=b''):
    ctx = zmq.Context()
    radio = ctx.socket(zmq.RADIO)
    radio.connect('udp://127.0.0.1:6000')
    send = lambda: radio.send(msgpack.packb({
        'src': 'udp://127.0.0.1:6001',
        'gamepads': {0: gamepad.as_dict()},
    }), copy=False, group=group)
    try:
        while True:
            await asyncio.get_running_loop().run_in_executor(None, send)
            await asyncio.sleep(0.05)
    finally:
        radio.close()


def main(screen):
    screen.clear()
    curses.curs_set(0)
    curses.init_pair(Gamepad.BUTTON_ACTIVE, curses.COLOR_GREEN, curses.COLOR_BLACK)
    gamepad = Gamepad()
    client = RuntimeClient()
    dgram_sender = threading.Thread(target=lambda: asyncio.run(send_datagrams(gamepad, client)), daemon=True)
    dgram_sender.start()

    while True:
        screen.erase()
        screen.addstr(1, 2, 'Dawn Console (CTRL + C to quit)')
        screen.addstr(3, 2, 'Gamepad 0')
        draw_gamepad(screen, gamepad)
        screen.refresh()
        key = screen.getkey()
        gamepad.update(key)


@click.command()
def cli(**options):
    curses.wrapper(main)


if __name__ == '__main__':
    cli()


# def send(client, payload):
#     print('[send] =>', payload)
#     client.send(msgpack.packb(payload))
#
#
# async def recv(client):
#     payload = msgpack.loads(await client.recv(), raw=False)
#     print('[recv] =>', payload)
#     return payload
#
#
# async def main():
#     ctx = Context()
#     client = ctx.socket(zmq.REQ)
#     client.connect('tcp://127.0.0.1:6002')
#     print('Connected to host')
#
#     send(client, {'type': 'set_match', 'alliance': 'blue', 'mode': 'auto'})
#     await recv(client)
#     await asyncio.sleep(5)
#     send(client, {'type': 'set_match', 'alliance': 'blue', 'mode': 'idle'})
#     await recv(client)
#     # send(client, {'type': 'run_challenge', 'seed': 1, 'challenges': ['double']*2})
#     # await recv(client)
#
#     # Device aliases
#     # send(client, {'type': 'set_alias', 'alias': {'name': 'left_drive', 'uid': 100}})
#     # await recv(client)
#     # # await asyncio.sleep(1)
#     # send(client, {'type': 'set_alias', 'alias': {'name': 'right_drive', 'uid': 101}})
#     # await recv(client)
#     # # await asyncio.sleep(1)
#     # send(client, {'type': 'del_alias', 'alias': {'name': 'right_drive'}})
#     # await recv(client)
#     # send(client, {'type': 'list_aliases'})
#     # await recv(client)
#
#     client.close()
#
#
# async def mock_runtime(ctx):
#     await asyncio.sleep(0.5)
#     dish = ctx.socket(zmq.DISH)
#     # dish.bind('udp://*:6000')
#     dish.bind('udp://*:6001')
#     dish.join(GROUP)
#     while True:
#         payload = msgpack.unpackb(await asyncio.get_running_loop().run_in_executor(None, lambda: dish.recv(copy=False)))
#         print('[recv]', payload)
#     dish.close()
#
#
# async def udp_main():
#     ctx = zmq.Context()
#     # await flood(ctx)
#     await asyncio.gather(mock_runtime(ctx), flood(ctx))
