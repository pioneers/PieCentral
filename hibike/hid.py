import os
import sys

import usb.core
import time


class HIDWrapper(object):
    """Handles low level communication over the USB protocol"""
    VENDOR_ID = 0x2341
    PRODUCT_ID = 0x8037

    def __init__(self, device, interface_num, endpoint_address):
        self.device = device
        self.interface_num = interface_num
        self.endpoint_address = endpoint_address

        self.device.set_configuration()
        self.device.reset()

    @classmethod
    def open_first(cls, vendor_id=VENDOR_ID, product_id=PRODUCT_ID):
        for args in cls.find_hid_endpoints(vendor_id, product_id):
            return HIDWrapper(*args)

        raise usb.USBError("Could not find any device (vendor_id={}, product_id={})".format(vendor_id, product_id))

    @classmethod
    def open_all(cls, vendor_id=VENDOR_ID, product_id=PRODUCT_ID):
        res = []
        for args in cls.find_hid_endpoints(vendor_id, product_id):
            try:
                res.append(HIDWrapper(*args))
            except usb.USBError as e:
                print("WARNING: Skipping device due to error:", e)
                continue

        return res

    @staticmethod
    def find_hid_endpoints(vendor_id, product_id):
        for device in usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id):
            for cfg in device:
                for interface_num, interface in enumerate(cfg):
                    if device.is_kernel_driver_active(interface.bInterfaceNumber):
                        try:
                            device.detach_kernel_driver(interface.bInterfaceNumber)
                        except usb.core.USBError as e:
                            print("Could not detach kernel driver from interface({}): {}".format(interface.bInterfaceNumber, str(e)))
                            continue

                    if interface.bInterfaceClass != 0x3: # HID
                        continue

                    # Our firmware creates an interface with a single HID endpoint
                    # We'll need the interface number and endpoint address to use
                    # the device
                    in_endpoint = interface[0]

                    yield device, interface_num, in_endpoint.bEndpointAddress

    def write(self, data):
        while True:
            try:
                return self.device.ctrl_transfer(0x21, 0x09, 0x0200, self.interface_num, data)
            except usb.core.USBError as e:
                time.sleep(0.05)

    def read(self, maximum_len):
        return self.device.read(self.endpoint_address, maximum_len)


def test_one():
    device = HIDWrapper.open_first()

    while True:
        res = device.write(b"0123456789asdf")
        print("Write result", res)

        res = device.read(200)
        print("Read result", res)

        time.sleep(0.1)

def test_many():
    devices = HIDWrapper.open_all()
    print('devices', devices)

    while True:
        for i, device in enumerate(devices):
            res = device.write(b"0123456789asdf")
            print("{}/{} Write result".format(i+1, len(devices)), res)

            res = device.read(200)
            print("{}/{} Read result".format(i+1, len(devices)), res)

        time.sleep(0.1)



if __name__ == '__main__':
    test_many()
