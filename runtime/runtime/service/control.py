import asyncio
import msgpack
import zmq.asyncio
from runtime.service.base import Service
import aio_msgpack_rpc as rpc





class ControlService(Service):
    async def get_version(self):
        return 10

    async def get_devices(self):
        pass

    async def set_device_name(self, uid: str, name: str):
        pass

    async def del_device_name(self, uid: str):
        pass

    async def main(self):
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.REP)
        socket.bind('tcp://*:8120')

        while True:
            print(await socket.poll(10))
            msg = msgpack.loads(await socket.recv())
            print(msg)
            await socket.send(msgpack.dumps({'i': msg[b'i'] + 1}))
