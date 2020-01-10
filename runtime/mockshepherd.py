#!/usr/bin/env python3

import asyncio
import msgpack
import zmq
import zmq.asyncio

async def main():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://127.0.0.1:6003')
    socket.subscribe(b'')
    while True:
        packet = await socket.recv()
        print(packet)

if __name__ == '__main__':
    asyncio.run(main())
