import asyncio
import threading
import time
import unittest
from runtime.util import AsyncThread, AsyncTimer


class TestAsyncThread(unittest.TestCase):
    name = 'asyncio-thread'

    def test_basic_start_join(self):
        ok = False
        async def target(self, x, y=1):
            # FIXME: using `self.assert*` methods don't seem to work here.
            nonlocal ok
            if x == 2 and y == 2:
                ok = True
        thread = AsyncThread(name=self.name, target=target, args=(self, 2,),
                             kwargs={'y': 2})
        thread.start()
        thread.join()
        self.assertTrue(ok)

    def test_stop(self):
        ready = threading.Event()
        async def target():
            while True:
                await asyncio.sleep(1)
                ready.set()
        thread = AsyncThread(name=self.name, target=target)
        thread.start()
        ready.wait()
        thread.stop()
        thread.join()


class TestAsyncTimer(unittest.TestCase):
    def setUp(self):
        self.timestamps = []

    async def add_timestamp(self):
        self.timestamps.append(time.time())

    def test_stop(self):
        async def callback():
            await self.add_timestamp()
            return True
        async def main():
            timer = AsyncTimer(callback, 0.05)
            await timer.run()
        asyncio.run(main())
        self.assertEqual(len(self.timestamps), 1)

    def test_timing(self):
        async def stop(timer):
            await asyncio.sleep(0.21)
            timer.stop()
        async def main():
            timer = AsyncTimer(self.add_timestamp, 0.05)
            await asyncio.gather(timer.run(), stop(timer))
        asyncio.run(main())
        self.assertEqual(len(self.timestamps), 5)
        for start, end in zip(self.timestamps[:-1], self.timestamps[1:]):
            self.assertAlmostEqual(end - start, 0.05, delta=0.002)


if __name__ == '__main__':
    unittest.main()
