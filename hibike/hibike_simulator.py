import time, random
import threading
import multiprocessing
from . import hibike_message as hm
import queue

__all__ = ["hibike_process"]

fake_uids = [0 << 72, 7 << 72]


uid_to_index = {}


def hibike_process(badThingsQueue, stateQueue, pipeFromChild):
    ports = ['0', '1']
    serials = [int(port) for port in ports]

    # each device has it's own write thread, with it's own instruction queue
    instruction_queues = [queue.Queue() for _ in ports]

    # since this is a simulation and there are no real devices, this is how the write threads interface with the read threads
    fake_device_queues = [queue.Queue() for _ in ports]

    # each device has one write thread that receives instructions from the main thread and writes to devices
    write_threads = [DeviceWriteThread(ser, iq, fake_device_queue) for ser, iq, fake_device_queue in zip(serials, instruction_queues, fake_device_queues)]
    
    # each device has a read thread that reads from devices and writes directly to stateManager
    read_threads = [DeviceReadThread(ser, None, stateQueue, fake_device_queue) for ser, fake_device_queue in zip(serials, fake_device_queues)]
    
    for read_thread in read_threads:
        read_thread.start()
    for write_thread in write_threads:
        write_thread.start()

    # the main thread reads instructions from statemanager and forwards them to the appropriate device write threads
    while True:
        instruction, args = pipeFromChild.recv()
        if instruction == "enumerate_all":
            for instruction_queue in instruction_queues:
                instruction_queue.put(("ping", []))
        elif instruction == "subscribe_device":
            uid = args[0]
            if uid in uid_to_index:
                instruction_queues[uid_to_index[uid]].put(("subscribe", args))

class DeviceWriteThread(threading.Thread):

    def __init__(self, ser, instructionQueue, fake_device_queue):
        self.ser = ser
        self.queue = instructionQueue
        self.fake_device_queue = fake_device_queue
        super().__init__()

    def run(self):
        while True:
            instruction = self.queue.get()
            self.fake_device_queue.put(instruction)

class DeviceReadThread(threading.Thread):

    def __init__(self, ser, errorQueue, stateQueue, fake_device_queue):
        self.ser = ser
        self.errorQueue = errorQueue
        self.stateQueue = stateQueue
        self.fake_device_queue = fake_device_queue
        self.delay = 0
        self.params = []

        self.fake_subscription_thread = FakeSubscriptionThread(fake_uids[self.ser], 0, [], self.fake_device_queue)
        self.fake_subscription_thread.start()
        super().__init__()

    def run(self):
        while True:
            instruction, args = self.fake_device_queue.get()
            res = None
            if instruction == "ping":
                uid, delay, params = fake_uids[self.ser], self.delay, self.params
                uid_to_index[uid] = self.ser
                res = ["device_subscribed", [uid, delay, params]]
            elif instruction == "subscribe":
                uid, delay, params = tuple(args)
                uid_to_index[uid] = self.ser
                res = ["device_subscribed", [uid, delay, params]]

                self.fake_subscription_thread.quit = True
                self.fake_subscription_thread.join()
                self.fake_subscription_thread = FakeSubscriptionThread(uid, delay, params, self.fake_device_queue)
                self.fake_subscription_thread.start()
            elif instruction == "device_values":
                res = [instruction, args]

            self.stateQueue.put(res)

class FakeSubscriptionThread(threading.Thread):

    def __init__(self, uid, delay, params, fake_device_queue):
        self.uid = uid
        self.delay = delay
        self.params = params
        self.fake_device_queue = fake_device_queue
        self.quit = False
        super().__init__()

    def run(self):
        if self.delay != 0:
            while True:
                if self.quit:
                    return
                time.sleep(self.delay / 1000.0)
                param_types = [hm.paramMap[hm.uid_to_device_id(self.uid)][param][1] for param in self.params]
                params_and_values = {}
                for param, param_type in zip(self.params, param_types):
                    if param_type in ("bool", ):
                        params_and_values[param] = random.choice([True, False])
                    elif param_type in ("uint8_t", "int8_t", "uint16_t", "int16_t", "uint32_t", "int32_t", "uint64_t", "int64_t"):
                        params_and_values[param] = random.randrange(256)
                    else:
                        params_and_values[param] = random.random()
                self.fake_device_queue.put(("device_values", [self.uid, list(params_and_values.items())]))


#############
## TESTING ##
#############

if __name__ == "__main__":
    pipeToChild, pipeFromChild = multiprocessing.Pipe()
    badThingsQueue = multiprocessing.Queue()
    stateQueue = multiprocessing.Queue()
    newProcess = multiprocessing.Process(target=hibike_process, name="hibike_sim", args=[badThingsQueue, stateQueue, pipeFromChild])
    newProcess.daemon = True
    newProcess.start()
    pipeToChild.send(["enumerate_all", []])
    print(stateQueue.get())
    print(stateQueue.get())
    pipeToChild.send(["subscribe_device", [0, 1000, ["switch0", "switch2"]]])
    print(stateQueue.get())
    while True:
        print(stateQueue.get())
