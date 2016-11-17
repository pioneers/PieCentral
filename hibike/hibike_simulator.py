import time, random
import threading
import multiprocessing
import queue

from hibike_util import *

DETERMINISTIC_MODE = True

fake_uids = [0 << 72, 7 << 72]

# This is what actually "knows" about. Only updated after enumeration
uid_to_queue = {}


def hibike_process(badThingsQueue, stateQueue, pipeFromChild):
    devices = [FakeDevice(uid, stateQueue) for uid in fake_uids]
    for device in devices:
        device.start()

    # the main thread reads instructions from statemanager and forwards them to the appropriate device write threads
    while True:
        instruction, args = pipeFromChild.recv()
        if instruction == "enumerate_all":
            for device in devices:
                device.instruction_queue.put(("ping", []))
        elif instruction == "subscribe_device":
            uid = args[0]
            if uid in uid_to_queue:
                uid_to_queue[uid].put(("subscribe", args))
            else:
                print('not found uid')

class FakeDevice():
    def __init__(self, uid, stateQueue):
        self.uid = uid
        self.stateQueue = stateQueue

        # Hibike doesn't actually know about these queues. They are here
        # to simulate the hardware serial ports.
        self.instruction_queue = queue.Queue()
        self.fake_device_queue = queue.Queue()
        self.fake_device_readings = queue.Queue()

    def start(self):
        fakeWriteThread = threading.Thread(
            target=runDeviceWrite,
            args=(self.instruction_queue, self.fake_device_queue),
            daemon=True)
        fakeReadThread = threading.Thread(
            target=runDeviceRead,
            args=(self.fake_device_readings, self.stateQueue, self.instruction_queue),
            daemon=True)
        fakeDeviceThread = threading.Thread(
            target=runFakeSubscription,
            args=(self.uid, self.fake_device_queue, self.fake_device_readings),
            daemon=True)

        threads = [fakeWriteThread, fakeReadThread, fakeDeviceThread]
        for thread in threads:
            thread.start()

def runDeviceWrite(instruction_queue, fake_device_queue):
    """instruction_queue is input
    fake_device_queue is output to smart sensor
    """
    while True:
        instruction, args = instruction_queue.get()

        if instruction == "ping":
            fake_device_queue.put(0)
        elif instruction == "subscribe":
            uid, delay, params = args
            fake_device_queue.put(delay)
            fake_device_queue.put(params)

def runDeviceRead(fake_device_readings, stateQueue, instruction_queue):
    while True:
        result, values = fake_device_readings.get()
        res = None
        if result == "device_values":
            res = (result, values)
        elif result == "device_subscribed":
            uid = values[0]
            if uid in uid_to_queue:
                del uid_to_queue[uid]
            uid_to_queue[uid] = instruction_queue
            res = (result, values)
        else:
            print("Some error code received")
            print(result, values)

        if res is not None:
            stateQueue.put(res)

def runFakeSubscription(uid, fake_device_queue, fake_device_readings):
    """fake_device_queue is input commands
    fake_device_readings is output of fake readings
    """
    timeout = None
    new_delay = False
    while True:
        try:
            delay = fake_device_queue.get(block=True, timeout=timeout)
            new_delay = True
        except queue.Empty:
            pass
        # Simulate enumeration
        if delay == 0:
            params = list(paramMap[uid_to_device_id(uid)].keys())
            fake_device_readings.put(("device_subscribed", [uid, 0, params]))
        # Simulate subscription
        elif delay > 0:
            if new_delay:
                params = fake_device_queue.get()
            param_types = [paramMap[uid_to_device_id(uid)][param][1] for param in params]
            params_and_values = {}
            if DETERMINISTIC_MODE:
                for param, param_type in zip(params, param_types):
                    if param_type in ("bool", ):
                        params_and_values[param] = True
                    elif param_type in ("uint8_t", "int8_t", "uint16_t", "int16_t", "uint32_t", "int32_t", "uint64_t", "int64_t"):
                        params_and_values[param] = 123
                    else:
                        params_and_values[param] = 101
            else:
                for param, param_type in zip(params, param_types):
                    if param_type in ("bool", ):
                        params_and_values[param] = random.choice([True, False])
                    elif param_type in ("uint8_t", "int8_t", "uint16_t", "int16_t", "uint32_t", "int32_t", "uint64_t", "int64_t"):
                        params_and_values[param] = random.randrange(256)
                    else:
                        params_and_values[param] = random.random()
            fake_device_readings.put(("device_values", [uid, list(params_and_values.items())]))
            timeout = delay / 1000.0
            new_delay = False
        else:
            print("Invalid negative delay: {:d}".format(delay))

#############
## TESTING ##
#############

if __name__ == "__main__":
    DETERMINISTIC_MODE = False
    pipeToChild, pipeFromChild = multiprocessing.Pipe()
    badThingsQueue = multiprocessing.Queue()
    stateQueue = multiprocessing.Queue()
    newProcess = multiprocessing.Process(target=hibike_process, name="hibike_sim", args=[badThingsQueue, stateQueue, pipeFromChild])
    newProcess.daemon = True
    newProcess.start()
    print("enumerating")
    pipeToChild.send(["enumerate_all", []])
    print(stateQueue.get())
    print(stateQueue.get())
    print("sending pipeToChild")
    pipeToChild.send(["subscribe_device", [0, 1000, ["switch0", "switch2"]]])
    print("done sending pipe"   )
    while True:
        print(stateQueue.get())
