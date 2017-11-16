"""
Unit tests for functions in hibike_message.
"""


import unittest
import random
import queue
import time
import threading

import serial

import hibike_message
import spawn_virtual_devices
from hibike_tests.utils import run_with_random_data

DEVICE_TYPES = list(hibike_message.DEVICES)


def random_uid():
    """ Generate a random UID. """
    uid_type = random.choice(DEVICE_TYPES)
    return uid_type << 72 | random.getrandbits(72)


def random_params(device_id):
    """ Get a random sampling of parameters for a particular DEVICE_TYPE. """
    all_params = hibike_message.all_params_for_device_id(device_id)
    sample_length = random.randrange(len(all_params) + 1)
    params = random.sample(all_params, sample_length)
    return params


def random_values(device_id, params):
    """ Generate random valid values for PARAMS. """
    all_params = hibike_message.DEVICES[device_id]["params"]
    values = []
    for param in params:
        param_index = 0
        for (idx, param_pack) in enumerate(all_params):
            if param_pack["name"] == param:
                param_index = idx
                break
        param_type = all_params[param_index]["type"]
        values.append(ParsingTests.VALUE_GENERATORS[param_type]())

    return values


class CobsTests(unittest.TestCase):
    """ Tests for COBS encoding and decoding. """
    @staticmethod
    def gen_cobs_data():
        """ Generate COBS-encodable data of a random length. """
        data_len = random.randrange(255)
        data = bytearray()

        for _ in range(data_len):
            data.append(random.randrange(256))

        return (data, )

    def test_encode_decode(self):
        """ Test basic functionality of cobs_encode/decode. """
        def assert_encode_decode_equal(data):
            """
            Check to make sure encode(decode) is idempotent.
            """
            encoded = hibike_message.cobs_encode(data)
            decoded = hibike_message.cobs_decode(encoded)
            self.assertEqual(data, decoded,
                             "{} encoded incorrectly".format(data))
        run_with_random_data(assert_encode_decode_equal, CobsTests.gen_cobs_data, times=100)


class FakeSerialPort(object):
    """ A fake serial port that acts as a queue. """
    def __init__(self):
        self._buf = queue.Queue()

    def write(self, byte_buf):
        """ Write BYTE_BUF into the queue. """
        for byte in byte_buf:
            self._buf.put(byte)

    def read(self, length=1):
        """ Read out LENGTH bytes from the queue. """
        buf = bytearray()
        for _ in range(length):
            buf.append(self._buf.get())
        return buf

    def drain(self):
        """ Read the contents of the queue into a bytearray. """
        contents = bytearray()
        while not self._buf.empty():
            contents.append(self._buf.get())
        return contents

    @property
    def in_waiting(self):
        """ The number of bytes in the queue. """
        return self._buf.qsize()


class ParamsTests(unittest.TestCase):
    """ Tests for encoding and decoding device parameters. """
    @staticmethod
    def gen_random_device_id_and_params():
        """ Generate a random device ID and set of parameters. """
        device_id = hibike_message.uid_to_device_id(random_uid())
        params = random_params(device_id)
        return (device_id, params)

    def test_idempotence(self):
        """
        Check that encoding and decoding a random set of parameters
        is idempotent.
        """
        def assert_params_same(device_id, param_list):
            """
            Check that encoding and decoding PARAM_LIST produces
            the same result.
            """
            encoded = hibike_message.encode_params(device_id, param_list)
            decoded = hibike_message.decode_params(device_id, encoded)
            self.assertEqual(sorted(decoded), sorted(param_list),
                             "encoded/decoded param list {} not identical".format(param_list))

        run_with_random_data(assert_params_same,
                             self.gen_random_device_id_and_params, times=1000)


class ParsingTests(unittest.TestCase):
    """ Tests for parsing Hibike messages. """
    MESSAGE_GENERATORS = {packet_type: None for packet_type in hibike_message.MESSAGE_TYPES}
    VALUE_GENERATORS = {key: None for key in hibike_message.PARAM_TYPES}
    @classmethod
    def setUpClass(cls):
        cls.MESSAGE_GENERATORS["SubscriptionRequest"] = cls.gen_random_sub_request
        cls.MESSAGE_GENERATORS["DeviceRead"] = cls.gen_random_device_read
        cls.MESSAGE_GENERATORS["HeartbeatResponse"] = cls.gen_random_heartbeat_response
        cls.MESSAGE_GENERATORS["SubscriptionResponse"] = cls.gen_random_sub_response
        cls.MESSAGE_GENERATORS["DeviceData"] = cls.gen_random_device_data
        cls.MESSAGE_GENERATORS["DeviceWrite"] = cls.gen_random_device_write
        cls.VALUE_GENERATORS["bool"] = lambda: random.randrange(2) == 0
        cls.VALUE_GENERATORS["uint8_t"] = lambda: random.randrange(256)
        cls.VALUE_GENERATORS["int8_t"] = lambda: random.randrange(-128, 128)
        cls.VALUE_GENERATORS["uint16_t"] = lambda: random.randrange(2 ** 16)
        cls.VALUE_GENERATORS["int16_t"] = lambda: random.randrange(-(2 ** 15), 2 ** 15)
        cls.VALUE_GENERATORS["uint32_t"] = lambda: random.randrange(2 ** 32)
        cls.VALUE_GENERATORS["int32_t"] = lambda: random.randrange(-(2 ** 31), 2 ** 31)
        cls.VALUE_GENERATORS["uint64_t"] = lambda: random.randrange(2 ** 64)
        cls.VALUE_GENERATORS["int64_t"] = lambda: random.randrange(-(2 ** 63), 2 ** 63)
        cls.VALUE_GENERATORS["float"] = random.random

    @staticmethod
    def encode_packet(packet):
        """ Turn a HibikeMessage into an encoded packet. """
        fake_port = FakeSerialPort()
        hibike_message.send(fake_port, packet)
        return fake_port.drain()

    @staticmethod
    def gen_random_sub_request():
        """ Generate a random subscription request packet. """
        device_id = random.choice(DEVICE_TYPES)
        params = random_params(device_id)
        delay = random.randrange(100)
        msg = hibike_message.make_subscription_request(device_id, params, delay)
        return (ParsingTests.encode_packet(msg), )

    @staticmethod
    def gen_random_sub_response():
        """ Generate a random subscription response packet. """
        uid = random_uid()
        device_id = hibike_message.uid_to_device_id(uid)
        params = random_params(device_id)
        delay = random.randrange(100)
        msg = hibike_message.make_subscription_response(device_id, params, delay, uid)
        return (ParsingTests.encode_packet(msg), )

    @staticmethod
    def gen_random_device_read():
        """ Generate a random device read packet. """
        device_id = random.choice(DEVICE_TYPES)
        params = random_params(device_id)
        msg = hibike_message.make_device_read(device_id, params)
        return (ParsingTests.encode_packet(msg), )

    @staticmethod
    def gen_random_device_write():
        """ Generate a random device write packet. """
        device_id = random.choice(DEVICE_TYPES)
        params = random_params(device_id)
        values = random_values(device_id, params)
        msg = hibike_message.make_device_write(device_id, zip(params, values))
        return (ParsingTests.encode_packet(msg), )

    @staticmethod
    def gen_random_device_data():
        """ Generate a random device data packet. """
        device_id = random.choice(DEVICE_TYPES)
        params = random_params(device_id)
        values = random_values(device_id, params)
        params_and_values = [(param, value) for param, value in zip(params, values)]
        msg = hibike_message.make_device_data(device_id, params_and_values)
        return (ParsingTests.encode_packet(msg), )

    @staticmethod
    def gen_random_heartbeat_response():
        """ Generate a heartbeat response with a random ID. """
        msg = hibike_message.make_heartbeat_response(random.randrange(256))
        return (ParsingTests.encode_packet(msg), )

    @staticmethod
    def gen_random_error():
        """ Generate an error packet with a random error code. """
        msg = hibike_message.make_error(random.randrange(256))
        return (ParsingTests.encode_packet(msg), )

    def test_parse_valid_packets(self):
        """
        Check that `hibike_message.parse_device_data` doesn't choke on valid
        packets.
        """
        def assert_parse_is_not_none(valid_packet):
            """ Assert that parsing a valid packet does not result in None. """
            parse_result = hibike_message.parse_bytes(valid_packet)
            self.assertIsNotNone(parse_result,
                                 "valid packet {} parsed as None".format(valid_packet))

        for func in self.MESSAGE_GENERATORS.values():
            if func is not None:
                run_with_random_data(assert_parse_is_not_none,
                                     func, times=100)

    def test_parse_bad_checksum(self):
        """ Packets with bad checksums should not be parsed. """
        def screw_up_checksum(valid_packet):
            """ Make the checksum of a valid packet wrong. """
            if valid_packet[-2] < 255:
                valid_packet[-2] += 1
            else:
                valid_packet[-2] -= 1
            return valid_packet

        def assert_parse_is_none(invalid_packet):
            """ Assert that parsing an invalid packet results in None. """
            parse_result = hibike_message.parse_bytes(invalid_packet)
            self.assertIsNone(parse_result,
                              "packet with bad checksum parsed: {}".format(invalid_packet))

        for func in self.MESSAGE_GENERATORS.values():
            if func is not None:
                # pylint: disable=cell-var-from-loop
                wrapped_func = lambda: (screw_up_checksum(*func()), )
                run_with_random_data(assert_parse_is_none, wrapped_func, times=100)

    def test_parse_idempotence(self):
        """ Check that parsing an encoded packet is idempotent. """
        def assert_parse_idempotent(valid_packet):
            """
            Check that parsing and encoding VALID_PACKET results in
            the same packet.
            """
            parse_result = hibike_message.parse_bytes(valid_packet)
            encoded = self.encode_packet(parse_result)
            self.assertEqual(valid_packet, encoded,
                             "parse not idempotent for {}".format(valid_packet))

        for func in self.MESSAGE_GENERATORS.values():
            if func is not None:
                run_with_random_data(assert_parse_idempotent, func, times=100)


class BlockingReadGeneratorTests(unittest.TestCase):
    """ Tests for blocking_read_generator. """
    DUMMY_DEVICE_TYPE = "LimitSwitch"
    STOP_TIMEOUT = 2

    def setUp(self):
        self.dummy_device = \
            serial.Serial(spawn_virtual_devices.spawn_device(self.DUMMY_DEVICE_TYPE))
        self.dummy_dev_id = hibike_message.device_name_to_id(self.DUMMY_DEVICE_TYPE)
        self.dummy_params = hibike_message.all_params_for_device_id(self.dummy_dev_id)
        # Wait for the device to become active
        time.sleep(1)

    def test_stop_event(self):
        """
        Make sure that triggering the stop event prevents
        additional reads
        """
        hibike_message.send(self.dummy_device,
                            hibike_message.make_subscription_request(self.dummy_dev_id,
                                                                     self.dummy_params, 40))
        start_time = time.time()
        stop_event = threading.Event()
        for _ in hibike_message.blocking_read_generator(self.dummy_device, stop_event):
            stop_event.set()
            self.assertLessEqual(time.time() - start_time, self.STOP_TIMEOUT,
                                 "blocking_read_generator didn't stop when stop_event triggered")

    def test_read_device_data(self):
        """ Check that DeviceData packets are received and decoded. """
        start_time = time.time()
        hibike_message.send(self.dummy_device,
                            hibike_message.make_subscription_request(self.dummy_dev_id,
                                                                     self.dummy_params, 40))
        for packet in hibike_message.blocking_read_generator(self.dummy_device):
            if packet.get_message_id() == hibike_message.MESSAGE_TYPES["DeviceData"]:
                return
            self.assertLessEqual(time.time() - start_time, self.STOP_TIMEOUT,
                                 "did not read DeviceData packet before timeout")
