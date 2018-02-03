import asyncio

async def read_serial(delay):
    await asyncio.sleep(delay)
    return delay

async def device_read2():
    while True:
        val = await read_serial(1)
        print("DEV delay_1 " + str(val))

async def device_read():
    while True:
        val = await read_serial(3)
        print("DEV delay_3 " + str(val))

def foo(future):
    print(future.result())

def main():
    # start multiple "threads" each which read from a serial connection
    # read data from each of these
    loop = asyncio.get_event_loop()
    loop.create_task(device_read())
    loop.create_task(device_read2())
    # future.add_done_callback(foo)

    loop.run_forever()


if __name__ == '__main__':
    main()
