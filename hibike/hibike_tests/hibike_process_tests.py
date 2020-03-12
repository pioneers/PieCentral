"""
Unit tests for functions in hibike_process.
"""
import asyncio
import os
import random
import sys
import time
import unittest

import aioprocessing
import serial

from spawn_virtual_devices import spawn_device, get_virtual_ports
from hibike_process import hotplug_async
from hibike_tests.utils import AsyncTestCase
import hibike_message as hm
from hibike_tester import Hibike

def add_runtime_to_path():
    """
    Enable import of runtime modules.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    parent_path = path.rstrip("hibike_tests").rstrip("hibike/")
    runtime = os.path.join(parent_path, "runtime")
    sys.path.insert(1, runtime)


add_runtime_to_path()
# We must import runtimeUtil to deserialize error messages
# pylint: disable=import-error, wrong-import-position, unused-import
import runtimeUtil




VIRTUAL_DEVICE_STARTUP_TIME = 2
VIRTUAL_DEVICE_CONFIG_FILE = "virtual_devices.txt"


def spawn_virtual_devices(device_types):
    """
    Spawn some virtual devices, wait for them to spin up,
    then tell Hibike about them.

    :param: device_types the types of the devices to spawn
    """
    device_ports = []
    for dev_type in device_types:
        device_ports.append(spawn_device(dev_type))
    time.sleep(VIRTUAL_DEVICE_STARTUP_TIME)
    write_out_virtual_devices(device_ports)


def write_out_virtual_devices(device_ports):
    """
    Tell Hibike about virtual devices located on serial ports.
    """
    with open(VIRTUAL_DEVICE_CONFIG_FILE, "w") as vdev_file:
        vdev_file.write(" ".join(device_ports))
        vdev_file.flush()


class BasicHotplugTests(AsyncTestCase):
    """
    Tests for `hotplug_async`.
    """
    VIRTUAL_DEVICE_TYPES = ["LimitSwitch", "YogiBear", "YogiBear",
                            "RFID", "BatteryBuzzer"]
    IDENTIFY_TIMEOUT = 5

    def setUp(self):
        super(BasicHotplugTests, self).setUp()
        self.devices = {}
        self.error_queue = asyncio.Queue(loop=self.loop)
        self.state_queue = aioprocessing.AioQueue()

    def identify_devices(self):
        """
        Try to identify virtual devices.
        """
        hotplug = self.loop.create_task(hotplug_async(self.devices, {}, self.error_queue,
                                                      self.state_queue, self.loop))
        self.run_until_timeout(hotplug, self.IDENTIFY_TIMEOUT)

    def assert_all_devices_identified(self, identified_devices, msg=None):
        """
        Assert that IDENTIFIED_DEVICES contains all devices in
        VIRTUAL_DEVICE_TYPES.
        """
        device_ids = map(hm.uid_to_device_id, identified_devices)
        found_types = map(lambda dev: hm.DEVICES[dev]["name"], device_ids)
        self.assertListEqual(sorted(self.VIRTUAL_DEVICE_TYPES), sorted(found_types), msg)

    def test_detect_devices(self):
        """ Test detection of valid devices. """
        spawn_virtual_devices(self.VIRTUAL_DEVICE_TYPES)
        self.identify_devices()
        self.assert_all_devices_identified(self.devices, "did not identify all sensors")

    def test_detect_no_devices(self):
        """ Make sure that we don't detect empty serial ports as sensors. """
        ports = []
        for _ in range(5):
            ports.append(serial.Serial(get_virtual_ports()[1]))
        write_out_virtual_devices(list(map(lambda p: p.name, ports)))
        self.identify_devices()
        self.assertEqual(self.devices, {}, "found smart sensor where there was none")

    def test_detect_some_devices(self):
        """
        Try detecting some devices when there are also empty
        serial ports.
        """
        ports = []
        devices = []
        for _ in range(5):
            ports.append(serial.Serial(get_virtual_ports()[1]))
        for vdev_type in self.VIRTUAL_DEVICE_TYPES:
            devices.append(serial.Serial(spawn_device(vdev_type)))
        write_out_virtual_devices(list(map(lambda d: d.name, devices)))
        time.sleep(VIRTUAL_DEVICE_STARTUP_TIME)
        self.identify_devices()
        self.assert_all_devices_identified(self.devices,
                                           "identified devices differs from spawned devices")


class ReadWriteTests(unittest.TestCase):
    """
    Test reading from and writing to devices.
    """
    VIRTUAL_DEVICE_TYPES = ["RFID", "LimitSwitch", "BatteryBuzzer",
                            "YogiBear", "YogiBear", "YogiBear"]
    HIBIKE_STARTUP_TIME = 2
    # Reads and writes take time to take effect
    READ_WRITE_DELAY = 0.25
    # Reads and writes can ocasionally fail; for reliability,
    # do them multiple times
    READ_WRITE_ATTEMPTS = 10

    def setUp(self):
        spawn_virtual_devices(self.VIRTUAL_DEVICE_TYPES)
        self.hibike = Hibike()
        time.sleep(self.HIBIKE_STARTUP_TIME)
        self.hibike.enumerate()

    def tearDown(self):
        self.hibike.terminate()

    def write(self, uid: int, params_and_values):
        """
        Send ``params_and_values`` to Hibike for writing.
        """
        for _ in range(self.READ_WRITE_ATTEMPTS):
            self.hibike.write(uid, params_and_values)
            time.sleep(self.READ_WRITE_DELAY)

    def read(self, uid: int, param: str):
        """
        Read ``param`` from Hibike and return the result.
        """
        for _ in range(self.READ_WRITE_ATTEMPTS):
            self.hibike.read(uid, [param])
        time.sleep(self.READ_WRITE_DELAY)
        return self.hibike.get_last_cached(uid, param)

    def test_write_then_read(self):
        """
        Writing a value to a device then reading from it should produce
        the same value.
        """
        for (uid, dev_type) in self.hibike.get_uids_and_types():
            if dev_type == "YogiBear":
                duty_cycle_val = random.random()
                self.write(uid, [("duty_cycle", duty_cycle_val)])
                hibike_value = self.read(uid, "duty_cycle")
                self.assertAlmostEqual(hibike_value, duty_cycle_val)

    def test_subscribe_write(self):
        """
        Test that subscribing sends up to date values.
        """
        self.hibike.subscribe_all()
        for (uid, dev_type) in self.hibike.get_uids_and_types():
            if dev_type == "YogiBear":
                self.write(uid, [("duty_cycle", random.random())])
                new_val = random.random()
                self.write(uid, [("duty_cycle", new_val)])
                new_hibike_val = self.hibike.get_last_cached(uid, "duty_cycle")
                self.assertAlmostEqual(new_hibike_val, new_val)

    def test_nonexistent_device(self):
        """
        Nonexistent device operations should error.
        """
        self.read("0x123456789", "duty_cycle")
        self.hibike.bad_things_queue.get(block=False)
