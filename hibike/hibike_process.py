import time, random
import threading
import multiprocessing
import hibike_message as hm
import queue
import glob
import serial
import os

__all__ = ["hibike_process"]


uid_to_index = {}

def hibike_process(badThingsQueue, stateQueue, pipeFromChild):

    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")

    try:
        virtual_device_config_file = os.path.join(os.path.dirname(__file__), "virtual_devices.txt")
        ports.extend(open(virtual_device_config_file, "r").read().split())
    except IOError:
        pass

    serials = [serial.Serial(port, 115200) for port in ports]

    # each device has it's own write thread, with it's own instruction queue
    instruction_queues = [queue.Queue() for _ in ports]

    # these threads receive instructions from the main thread and write to devices
    write_threads = [DeviceWriteThread(ser, iq) for ser, iq in zip(serials, instruction_queues)]

    # these threads receive packets from devices and write to statequeue
    read_threads = [DeviceReadThread(index, ser, iq, None, stateQueue) for index, (ser, iq) in enumerate(zip(serials, instruction_queues))]

    print(ports)

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
        elif instruction == "write_params":
            uid = args[0]
            if uid in uid_to_index:
                instruction_queues[uid_to_index[uid]].put(("write", args))
        elif instruction == "read_params":
            uid = args[0]
            if uid in uid_to_index:
                instruction_queues[uid_to_index[uid]].put(("read", args))            


class DeviceWriteThread(threading.Thread):

    def __init__(self, ser, instructionQueue):
        self.ser = ser
        self.queue = instructionQueue
        super().__init__()

    def run(self):
        while True:
            instruction, args = self.queue.get()

            if instruction == "ping":
                hm.send(self.ser, hm.make_ping())
            elif instruction == "subscribe":
                uid, delay, params = args
                hm.send(self.ser, hm.make_subscription_request(hm.uid_to_device_id(uid), params, delay))
            elif instruction == "read":
                uid, params = args
                hm.send(self.ser, hm.make_device_read(hm.uid_to_device_id(uid), params))
            elif instruction == "write":
                uid, params_and_values = args
                hm.send(self.ser, hm.make_device_write(hm.uid_to_device_id(uid), params_and_values))
            elif instruction == "die":
                return


class DeviceReadThread(threading.Thread):

    def __init__(self, index, ser, instructionQueue, errorQueue, stateQueue):
        self.index = index
        self.ser = ser
        self.instructionQueue = instructionQueue
        self.errorQueue = errorQueue
        self.stateQueue = stateQueue
        self.delay = 0
        self.params = []
        self.uid = None

        super().__init__()

    def run(self):
        while True:
            packet = hm.blocking_read(self.ser)
            message_type = packet.getmessageID()
            if message_type == hm.messageTypes["SubscriptionResponse"]:
                params, delay, uid = hm.parse_subscription_response(packet)
                self.uid = uid
                uid_to_index[uid] = self.index
                self.stateQueue.put(("device_subscribed", [uid, delay, params]))
            elif message_type == hm.messageTypes["DeviceData"]:
                if self.uid is not None:
                    params_and_values = hm.parse_device_data(packet, hm.uid_to_device_id(self.uid))
                    self.stateQueue.put(("device_values", params_and_values))
                else:
                    print("[HIBIKE] Port %s received data before enumerating!!!" % self.ser.port)


#############
## TESTING ##
#############

if __name__ == "__main__":

    # helper functions so we can spawn threads that try to
    def set_interval_sequence(functions, sec):
        def func_wrapper():
            set_interval_sequence(functions[1:] + functions[:1], sec)
            functions[0]()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def make_send_write(pipeToChild, uid, params_and_values):
        def helper():
            pipeToChild.send(["write_params", [uid, params_and_values]])
        return helper



    pipeToChild, pipeFromChild = multiprocessing.Pipe()
    badThingsQueue = multiprocessing.Queue()
    stateQueue = multiprocessing.Queue()
    newProcess = multiprocessing.Process(target=hibike_process, name="hibike_sim", args=[badThingsQueue, stateQueue, pipeFromChild])
    newProcess.daemon = True
    newProcess.start()
    pipeToChild.send(["enumerate_all", []])
    uids = set()
    while True:
        command, args = stateQueue.get()
        if command == "device_subscribed":
            uid = args[0]
            if uid not in uids:
                uids.add(uid)
                if hm.devices[hm.uid_to_device_id(uid)]["name"] == "TeamFlag":
                    set_interval_sequence([
                        make_send_write(pipeToChild, uid, [("led1", 1), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 1), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 1), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 1), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 1)]), 
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 1), ("yellow", 0)])
                        ], 0.1)
                elif hm.devices[hm.uid_to_device_id(uid)]["name"] == "YogiBear":
                    set_interval_sequence([
                        make_send_write(pipeToChild, uid, [("duty", 0),   ("forward", True)]),
                        make_send_write(pipeToChild, uid, [("duty", 50),  ("forward", True)]),
                        make_send_write(pipeToChild, uid, [("duty", 100), ("forward", True)]),
                        make_send_write(pipeToChild, uid, [("duty", 0),   ("forward", False)]),
                        make_send_write(pipeToChild, uid, [("duty", 50),  ("forward", False)]),
                        make_send_write(pipeToChild, uid, [("duty", 100), ("forward", False)])
                        ], 1)
                elif hm.devices[hm.uid_to_device_id(uid)]["name"] == "ServoControl":
                    set_interval_sequence([
                        make_send_write(pipeToChild, uid, [("servo0", 1), ("enable0", False), ("servo1", 21), ("enable1", True), ("servo2", 30), ("enable2", True), ("servo3", 8), ("enable3", True)]),
                        make_send_write(pipeToChild, uid, [("servo0", 5), ("enable0", False), ("servo1", 5), ("enable1", True), ("servo2", 5), ("enable2", True), ("servo3", 5), ("enable3", False)]),
                        make_send_write(pipeToChild, uid, [("servo0", 1), ("enable0", True), ("servo1", 26), ("enable1", True), ("servo2", 30), ("enable2", False), ("servo3", 17), ("enable3", True)]),
                        make_send_write(pipeToChild, uid, [("servo0", 13), ("enable0", False), ("servo1", 7), ("enable1", False), ("servo2", 24), ("enable2", True), ("servo3", 10), ("enable3", True)]),
                        make_send_write(pipeToChild, uid, [("servo0", 27), ("enable0", True), ("servo1", 2), ("enable1", False), ("servo2", 3), ("enable2", False), ("servo3", 14), ("enable3", False)]),
                        make_send_write(pipeToChild, uid, [("servo0", 20), ("enable0", True), ("servo1", 12), ("enable1", False), ("servo2", 20), ("enable2", False), ("servo3", 29), ("enable3", True)]),
                        ], 1)
                pipeToChild.send(["subscribe_device", [uid, 10, [param["name"] for param in hm.devices[hm.uid_to_device_id(uid)]["params"]]]])
        elif command == "device_values":
            print("%10.2f, %s" % (time.time(), str(args)))
