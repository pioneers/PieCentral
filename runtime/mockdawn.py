#!/usr/bin/env python3

import asyncio
import msgpack
import zmq
from zmq.asyncio import Context


async def main():
    ctx = Context()
    client = ctx.socket(zmq.REQ)
    client.connect('tcp://127.0.0.1:6002')
    print('Connected to host')
    client.send(msgpack.packb({}))
    # client.close()


if __name__ == '__main__':
    asyncio.run(main())
