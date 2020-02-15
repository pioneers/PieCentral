import unittest

from runtime.messaging import packet as packetlib


class TestPacketLibrary(unittest.TestCase):
    def setUp(self):
        pass

    def test_make_ping(self):
        self.assertEqual(packetlib.make_ping().encode(), b'\x10\x00\x10')

    def test_make_heartbeat_req(self):
        self.assertEqual(packetlib.make_heartbeat_req(0x00).encode(), b'\x17\x01\x00\x16')
        self.assertEqual(packetlib.make_heartbeat_req(0xFF).encode(), b'\x17\x01\xff\xe9')
        with self.assertRaises(OverflowError):
            packetlib.make_heartbeat_req(-0x01).encode()
        with self.assertRaises(OverflowError):
            packetlib.make_heartbeat_req(0x100).encode()

    def test_make_heartbeat_res(self):
        self.assertEqual(packetlib.make_heartbeat_res(0x00).encode(), b'\x18\x01\x00\x19')
        self.assertEqual(packetlib.make_heartbeat_res(0xFF).encode(), b'\x18\x01\xff\xe6')
        with self.assertRaises(OverflowError):
            packetlib.make_heartbeat_res(-0x01).encode()
        with self.assertRaises(OverflowError):
            packetlib.make_heartbeat_res(0x100).encode()


if __name__ == '__main__':
    unittest.main()
