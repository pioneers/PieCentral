#!/usr/bin/env python3

import asyncio
import msgpack
import zmq
import zmq.asyncio


async def sub():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://127.0.0.1:6001')
    socket.setsockopt(zmq.SUBSCRIBE, b'')
    while True:
        payload = msgpack.loads(await socket.recv())
        print(payload)


async def pub(period=1):
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.PUB)
    socket.bind('tcp://127.0.0.1:6000')
    i = 0
    while True:
        await socket.send_multipart([msgpack.dumps({'i': i})])
        print('Sent!')
        await asyncio.sleep(period)
        i += 1


async def main():
    await pub()
    # await sub()


if __name__ == '__main__':
    asyncio.run(main())
