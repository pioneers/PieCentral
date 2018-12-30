import ctypes
import unittest
import multiprocessing
import time
from runtime.buffer import SharedMemory, SharedLock, SensorBuffer, ParameterStatus
from runtime.devices import SensorStructure, Parameter


class TestSharedMemory(unittest.TestCase):
    def setUp(self):
        self.buf = SharedMemory('test', 8)

    def tearDown(self):
        del self.buf

    def test_zeroed(self):
        for byte in self.buf:
            self.assertEqual(byte, 0)

    def test_shared(self):
        def target(ready):
            ready.wait()
            buf = SharedMemory('test', 8)
            self.assertEqual(buf[0], 1)
            buf[0] = 2
        ready = multiprocessing.Event()
        child = multiprocessing.Process(target=target, args=(ready, ))
        child.start()
        self.assertEqual(self.buf[0], 0)
        self.buf[0] = 1
        ready.set()
        child.join()
        self.assertEqual(self.buf[0], 2)

    def test_out_of_bounds(self):
        with self.assertRaises(IndexError):
            print(self.buf[-9])
        with self.assertRaises(IndexError):
            print(self.buf[8])


class TestSharedLock(unittest.TestCase):
    def setUp(self):
        self.lock = SharedLock('test-lock')

    def tearDown(self):
        del self.lock

    def test_lock(self):
        def target(sync_ctr, unsync_ctr, n):
            lock = SharedLock('test-lock')
            for _ in range(n):
                unsync_ctr.value += 1
            for _ in range(n):
                with lock:
                    sync_ctr.value += 1
        sync_ctr = multiprocessing.Value('i', lock=False)
        unsync_ctr = multiprocessing.Value('i', lock=False)
        child_count, n = 4, 8000
        children = [multiprocessing.Process(target=target, args=(sync_ctr, unsync_ctr, n))
                    for _ in range(child_count)]
        for child in children:
            child.start()
        for child in children:
            child.join()
        self.assertEqual(sync_ctr.value, child_count*n)
        self.assertLess(unsync_ctr.value, child_count*n)


class TestSensorBuffer(unittest.TestCase):
    def setUp(self):
        self.PolarBear = SensorStructure.make_sensor_type('PolarBear', [
            Parameter('duty_cycle', ctypes.c_double, -1, 1, True, True),
        ])
        self.raw_buf = SensorBuffer('test-sensor', self.PolarBear)
        self.buf = self.PolarBear.from_buffer(self.raw_buf)
        self.one = b'\x00'*6 + b'\xf0?'

    def test_init(self):
        self.assertAlmostEqual(self.buf.duty_cycle, 0.0)
        self.assertEqual(self.raw_buf.get_value(0), b'\x00'*8)
        self.assertTrue(self.raw_buf.is_readable(0))
        self.assertTrue(self.raw_buf.is_writeable(0))
        self.assertFalse(self.raw_buf.is_dirty(0))

    def test_sensor_buf_write(self):
        before = time.time()
        self.raw_buf.set_value(0, self.one)
        after = time.time()
        self.assertTrue(self.raw_buf.is_dirty(0))
        self.assertAlmostEqual(self.buf.duty_cycle, 1.0)
        timestamp = self.buf.last_modified('duty_cycle')
        self.assertLess(before, timestamp)
        self.assertLess(timestamp, after)
        self.assertLess(after - before, 0.01)

    def test_struct_write(self):
        self.buf.duty_cycle = 1.0
        self.assertEqual(self.raw_buf.get_value(0), self.one)
        self.assertTrue(self.raw_buf.is_dirty(0))


if __name__ == '__main__':
    unittest.main()
