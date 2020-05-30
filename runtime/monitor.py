import asyncio
import aiozmq.rpc
import threading

class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    async def log(self, record):
        print(record)

async def main():
    handler = Handler()
    sub = await aiozmq.rpc.serve_pubsub(handler,
                                        subscribe=['debug', 'info', 'warn', 'warning', 'error', 'critical'],
                                        connect='tcp://127.0.0.1:6003',
                                        log_exceptions=True)
    print(f'Subscriber ready (threads={threading.active_count()})')
    await sub.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
