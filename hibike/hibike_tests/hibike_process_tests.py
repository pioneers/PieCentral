"""
Unit tests for functions in hibike_process.
"""
import unittest
import time
import serial
from spawn_virtual_devices import spawn_device, get_virtual_ports
from hibike_process import identify_smart_sensors
import hibike_message as hm

class IdentifySmartSensorsTests(unittest.TestCase):
    """
    Tests for `identify_smart_sensors`.
    """
    VIRTUAL_DEVICE_TYPES = ["LimitSwitch", "YogiBear", "YogiBear",
                            "RFID", "LineFollower", "BatteryBuzzer",
                            "Potentiometer"]
    VIRTUAL_DEVICE_STARTUP_TIME = 2
    def assert_all_devices_identified(self, identified_devices, msg=None):
        """
        Assert that IDENTIFIED_DEVICES contains all devices in
        VIRTUAL_DEVICE_TYPES.
        """
        device_ids = map(hm.uid_to_device_id, identified_devices.values())
        found_types = map(lambda dev: hm.DEVICES[dev]["name"], device_ids)
        self.assertListEqual(sorted(self.VIRTUAL_DEVICE_TYPES), sorted(found_types), msg)

    def test_detect_devices(self):
        """ Test detection of valid devices. """
        virtual_devices = []
        for vdev_type in self.VIRTUAL_DEVICE_TYPES:
            virtual_devices.append(serial.Serial(spawn_device(vdev_type)))
        # Wait for virtual devices to spin up
        time.sleep(self.VIRTUAL_DEVICE_STARTUP_TIME)
        found = identify_smart_sensors(virtual_devices)
        self.assert_all_devices_identified(found, "did not identify all sensors")

    def test_detect_no_devices(self):
        """ Make sure that we don't detect empty serial ports as sensors. """
        ports = []
        for _ in range(5):
            ports.append(serial.Serial(get_virtual_ports()[1]))

        found = identify_smart_sensors(ports)
        self.assertEqual(found, {}, "found smart sensor where there was none")

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
        time.sleep(self.VIRTUAL_DEVICE_STARTUP_TIME)
        found = identify_smart_sensors(ports + devices)
        self.assert_all_devices_identified(found,
                                           "identified devices differs from spawned devices")
