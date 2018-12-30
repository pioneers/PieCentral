import unittest
import threading
import time
from runtime.buffer import BinaryRingBuffer


class TestRingBuffer(unittest.TestCase):
    def setUp(self):
        self.buf = BinaryRingBuffer(8)

    def tearDown(self):
        del self.buf

    def test_simple_extend(self):
        self.assertEqual(len(self.buf), 0)
        with self.assertRaises(IndexError):
            self.buf[0]

        self.buf.extend(b'123\x00')
        self.assertEqual(len(self.buf), 4)
        self.assertEqual(self.buf[0], ord('1'))
        self.assertEqual(self.buf[3], ord('\x00'))
        with self.assertRaises(IndexError):
            self.buf[4]
        with self.assertRaises(IndexError):
            self.buf.extend(b'5678')

    def test_simple_read(self):
        self.buf.extend(b'\x0012\x0034\x00')
        self.assertEqual(self.buf.read(), b'')
        self.assertEqual(len(self.buf), 6)
        self.assertEqual(self.buf.read(), b'12')
        self.assertEqual(len(self.buf), 3)
        self.buf.extend(b'567\x00')
        self.assertEqual(len(self.buf), 7)
        self.assertEqual(self.buf.read(), b'34')
        self.assertEqual(self.buf.read(), b'567')
        self.assertEqual(len(self.buf), 0)

    def test_read_notify(self):
        read_time: int
        def target(buf):
            buf.extend(b'123\x00')
            nonlocal read_time
            read_time = time.time()
        child = threading.Thread(target=target, args=(self.buf,))
        child.start()
        self.assertEqual(self.buf.read(), b'123')
        self.assertLess(time.time() - read_time, 1e-3)
        child.join()


if __name__ == '__main__':
    unittest.main()
