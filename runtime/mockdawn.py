#!/usr/bin/env python3

import asyncio
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
    # send(client, {'type': 'set_match', 'alliance': 'blue', 'mode': 'auto'})
    # await recv(client)
    # send(client, {'type': 'set_match', 'alliance': 'blue', 'mode': 'idle'})
    # await recv(client)
    send(client, {'type': 'run_challenge', 'seed': 1})
    await recv(client)
    client.close()


if __name__ == '__main__':
    asyncio.run(main())
