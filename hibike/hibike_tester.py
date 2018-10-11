"""
Create a separate Hibike process, for testing.
"""
import threading
import time
import queue
from multiprocessing import Process, Pipe, Queue

import hibike_process
import hibike_message

class Hibike:
    """
    Interface to a separate Hibike process.
    """
    DEFAULT_DELAY = 100
    def __init__(self):
        self.bad_things_queue = Queue()
        self.state_queue = Queue()
        self.pipe_to_child, self.pipe_from_child = Pipe()
        self.hibike_process = Process(target=hibike_process.hibike_process,
                                      args=(self.bad_things_queue,
                                            self.state_queue, self.pipe_from_child))
        self.hibike_process.daemon = True
        self.hibike_process.start()
        self.uids = set()
        self.terminating = threading.Event()
        self.out_thread = threading.Thread(target=self.process_output)
        self.out_thread.start()
        self.device_values_cache = {}

    def process_output(self):
        """
        Processes the output uploaded to the state queue by te devices.

        If it's a subscription response from a device whose uid is not in
        self.uids, the uid will be added to self.uids.

        If it's a device disconnection from a device whose uid in self.uids,
        the uid will be removed from self.uids.

        If it's a device value, cache it in the dictionary.
        """
        while not self.terminating.is_set():
            try:
                command, data = self.state_queue.get(timeout=1)
            except queue.Empty:
                continue
            if command == "device_subscribed":
                uid = data[0]
                self.uids.add(uid)
            elif command == "device_disconnected":
                uid = data[0]
                self.uids.discard(uid)
            elif command == "device_values":
                for uid, params in data[0].items():
                    for key, value in params:
                        self.device_values_cache.setdefault(uid, {})[key] = value

    def get_last_cached(self, uid, param):
        """
        Get the last value of PARAM received from the device at UID.

        Precondition: a device_data with a UID, params, and values must have been
        received from the param before calling this function.
        """
        try:
            return self.device_values_cache[uid][param]
        except KeyError:
            print("Could not get parameter {} from {}".format(param, uid))
            return None

    def get_uids_and_types(self):
        """
        Returns a list of tuples of all of the uids of all devices that the
        HibikeCommunicator talks to. Tuple structure: (uid, device type name).
        """
        return [(uid, hibike_message.uid_to_device_name(uid)) for uid in self.uids]

    def enumerate(self):
        """
        Enumerate all devices.
        """
        self.pipe_to_child.send(["enumerate_all", []])

    def subscribe(self, uid, delay, params):
        """
        Subscribe to device UID, with DELAY delay, and parameters PARAMS.
        """
        self.pipe_to_child.send(["subscribe_device", [uid, delay, params]])

    def subscribe_all(self):
        """
        Subscribe to all devices with all parameters.
        """
        for uid in self.uids:
            dev_id = hibike_message.uid_to_device_id(uid)
            all_params = hibike_message.all_params_for_device_id(dev_id)
            readable_params = []
            for param in all_params:
                if hibike_message.readable(dev_id, param):
                    readable_params.append(param)
            self.pipe_to_child.send(["subscribe_device", [uid, self.DEFAULT_DELAY,
                                                          readable_params]])

    def write(self, uid, params_and_values):
        """
        Write PARAMS_AND_VALUES to the device at UID.
        """
        self.pipe_to_child.send(["write_params", [uid, params_and_values]])

    def read(self, uid, params):
        """
        Read PARAMS from the device at UID.
        """
        self.pipe_to_child.send(["read_params", [uid, params]])

    def disable(self):
        """
        Disable all attached devices.
        """
        self.pipe_to_child.send(["disable_all", []])

    def terminate(self):
        """
        Terminate the hibike process and clean up resources.
        """
        self.hibike_process.terminate()
        self.terminating.set()
        self.out_thread.join()

# pylint: disable=too-many-branches, too-many-statements
def run_test():
    comms = Hibike()
    time.sleep(3)
    device_info = comms.get_uids_and_types()
    for uid, device_type in device_info:
        print("Device info packet:", (uid, device_type))
        print("Type:", device_type)
        if device_type == "LimitSwitch":
            while True:
                comms.subscribe(uid, 100, ["switch0", "switch1", "switch2", "switch3"])
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, switch0 and switch1:")
                print(comms.get_last_cached(uid, "switch0"))
                print(comms.get_last_cached(uid, "switch1"))
                time.sleep(0.5)

        elif device_type == "LineFollower":
            while True:
                comms.subscribe(uid, 100, ["left", "center", "right"])
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, all params:")
                print(comms.get_last_cached(uid, "left"))
                print(comms.get_last_cached(uid, "right"))
                time.sleep(0.5)

        elif device_type == "Potentiometer":
            while True:
                comms.subscribe(uid, 100, ["pot0", "pot1", "pot2", "pot3"])
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, pot0 and pot2:")
                print(comms.get_last_cached(uid, "pot0"))
                print(comms.get_last_cached(uid, "pot1"))
                time.sleep(0.5)

        elif device_type == "Encoder":
            while True:
                comms.read(uid, ["rotation"])
                time.sleep(0.05)
                comms.read(uid, ["rotation"])
                time.sleep(0.05)
                comms.read(uid, ["rotation"])
                time.sleep(0.5)

        elif device_type == "BatteryBuzzer":
            while True:
                comms.subscribe(uid, 100, ["cell1", "cell2", "cell3", "calibrate"])
                time.sleep(0.05)
                comms.write(uid, ("calibrate", True))
                time.sleep(0.05)
                comms.write(uid, ("calibrate", False))
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, calibrate and cell2:")
                print(comms.get_last_cached(uid, "calibrate"))
                print(comms.get_last_cached(uid, "cell2"))
                time.sleep(0.5)

        elif device_type == "TeamFlag":
            while True:
                comms.subscribe(uid, 100, ["led1", "led2", "led3", "led4", "blue", "yellow"])
                time.sleep(0.05)
                comms.write(uid, [("led1", True), ("led2", True), ("led3", False),
                                  ("led4", False), ("blue", True), ("yellow", False)])
                time.sleep(0.05)
                comms.write(uid, [("led1", False), ("led2", False), ("led3", True),
                                  ("led4", True), ("blue", False), ("yellow", True)])
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, blue and yellow:")
                print(comms.get_last_cached(uid, "blue"))
                print(comms.get_last_cached(uid, "yellow"))
                time.sleep(0.5)

        elif device_type == "YogiBear":
            while True:
                comms.subscribe(uid, 100, ["duty", "forward"])
                time.sleep(0.05)
                comms.write(uid, [("duty", 100), ("forward", False)])
                time.sleep(0.05)
                comms.write(uid, [("duty", 50), ("forward", True)])
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, all params:")
                print(comms.get_last_cached(uid, "duty"))
                print(comms.get_last_cached(uid, "forward"))
                time.sleep(0.5)

        elif device_type == "ServoControl":
            while True:
                comms.subscribe(uid, 100, ["servo0", "enable0", "servo1", "enable1",
                                           "servo2", "enable2", "servo3", "enable3"])
                time.sleep(0.05)
                comms.write(uid, [("servo0", 3), ("enable0", False), ("servo1", 3),
                                  ("enable1", False), ("servo2", 3), ("enable2", True),
                                  ("servo3", 3), ("enable3", False)])
                time.sleep(0.05)
                comms.write(uid, [("servo0", 1), ("enable0", True), ("servo1", 26),
                                  ("enable1", True), ("servo2", 30), ("enable2", False),
                                  ("servo3", 17), ("enable3", True)])
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, servo1 and enable1:")
                print(comms.get_last_cached(uid, "servo1"))
                print(comms.get_last_cached(uid, "enable1"))
                time.sleep(0.5)

        elif device_type == "ExampleDevice":
            while True:
                comms.subscribe(uid, 100, ["kumiko", "hazuki", "sapphire", "reina",
                                           "asuka", "haruka", "kaori", "natsuki", "yuko",
                                           "mizore", "nozomi", "shuichi", "takuya",
                                           "riko", "aoi", "noboru"])
                time.sleep(0.05)
                comms.write(uid, [("kumiko", True), ("hazuki", 19), ("sapphire", 12),
                                  ("reina", 210), ("asuka", 105), ("haruka", 1005),
                                  ("kaori", 551), ("natsuki", 18002), ("yuko", 9001),
                                  ("mizore", 6.45), ("nozomi", 33.2875), ("takuya", 331),
                                  ("aoi", 7598)])
                time.sleep(0.05)
                comms.write(uid, [("kumiko", False), ("hazuki", 0), ("sapphire", 0),
                                  ("reina", 0), ("asuka", 0), ("haruka", 0), ("kaori", 0),
                                  ("natsuki", 0), ("yuko", 0), ("mizore", 0.0), ("nozomi", 0.0),
                                  ("takuya", 0), ("aoi", 0)])
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, kumiko and hazuki:")
                print(comms.get_last_cached(uid, "kumiko"))
                print(comms.get_last_cached(uid, "hazuki"))
                time.sleep(0.5)

        elif device_type == "RFID":
            while True:
                comms.subscribe(uid, 100, ["id", "detect_tag"])
                time.sleep(0.05)
                comms.read(uid, ["id"])
                time.sleep(0.05)
                print("Uid:", uid)
                print("Last cached, all params:")
                print(comms.get_last_cached(uid, "id"))
                print(comms.get_last_cached(uid, "detect_tag"))
                time.sleep(0.5)

        else:
            raise TypeError("ERROR: unknown device type detected")
