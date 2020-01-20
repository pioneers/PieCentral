#!/usr/bin/env python3

import asyncio
import functools
import msgpack
import zmq
from zmq.asyncio import Context


def send(client, payload):
    print('[send] =>', payload)
    client.send(msgpack.packb(payload))


async def recv(client):
    payload = msgpack.loads(await client.recv(), raw=False)
    print('[recv] =>', payload)
    return payload


async def main():
    ctx = Context()
    client = ctx.socket(zmq.REQ)
    client.connect('tcp://127.0.0.1:6002')
    print('Connected to host')

    send(client, {'type': 'set_match', 'alliance': 'blue', 'mode': 'auto'})
    await recv(client)
    await asyncio.sleep(5)
    send(client, {'type': 'set_match', 'alliance': 'blue', 'mode': 'idle'})
    await recv(client)
    # send(client, {'type': 'run_challenge', 'seed': 1, 'challenges': ['double']*2})
    # await recv(client)

    # Device aliases
    # send(client, {'type': 'set_alias', 'alias': {'name': 'left_drive', 'uid': 100}})
    # await recv(client)
    # # await asyncio.sleep(1)
    # send(client, {'type': 'set_alias', 'alias': {'name': 'right_drive', 'uid': 101}})
    # await recv(client)
    # # await asyncio.sleep(1)
    # send(client, {'type': 'del_alias', 'alias': {'name': 'right_drive'}})
    # await recv(client)
    # send(client, {'type': 'list_aliases'})
    # await recv(client)

    client.close()


GROUP = b''


async def flood(ctx):
    await asyncio.sleep(0.5)
    radio = ctx.socket(zmq.RADIO)
    radio.connect('udp://127.0.0.1:6000')
    i = 0
    while True:
        print('[send]', i)
        payload = msgpack.packb({
            'src': 'udp://127.0.0.1:6001',
            'gamepad': {
                0: {
                    'lx': 1.0,
                    'ly': -0.5,
                    'rx': 1.0,
                    'ry': -0.5,
                    'btn': 0b1111_1111_1111_1111_1111
                }
            }
        })
        send = lambda: radio.send(payload, copy=False, group=GROUP)
        await asyncio.get_running_loop().run_in_executor(None, send)
        await asyncio.sleep(0.05)
        i += 1
    radio.close()


async def mock_runtime(ctx):
    await asyncio.sleep(0.5)
    dish = ctx.socket(zmq.DISH)
    # dish.bind('udp://*:6000')
    dish.bind('udp://*:6001')
    dish.join(GROUP)
    while True:
        payload = msgpack.unpackb(await asyncio.get_running_loop().run_in_executor(None, lambda: dish.recv(copy=False)))
        print('[recv]', payload)
    dish.close()


async def udp_main():
    ctx = zmq.Context()
    # await flood(ctx)
    await asyncio.gather(mock_runtime(ctx), flood(ctx))


if __name__ == '__main__':
    asyncio.run(udp_main())
