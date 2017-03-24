import time, random
import threading
import multiprocessing
import hibike_message as hm
from hid import HIDWrapper as hid
import queue
import glob
import serial
import os
from platform import system

__all__ = ["hibike_process"]


uid_to_index = {}

def hibike_process(badThingsQueue, stateQueue, pipeFromChild):

    devices = hid.open_all()


    # each device has it's own write thread, with it's own instruction queue
    instruction_queues = [queue.Queue() for _ in devices]

    # these threads receive instructions from the main thread and write to devices
    write_threads = [threading.Thread(target=device_write_thread, args=(dev, iq)) for dev, iq in zip(devices, instruction_queues)]

    # these threads receive packets from devices and write to statequeue
    read_threads = [threading.Thread(target=device_read_thread, args=(index, dev, iq, None, stateQueue)) for index, (dev, iq) in enumerate(zip(devices, instruction_queues))]

    for read_thread in read_threads:
        read_thread.start()
    for write_thread in write_threads:
        write_thread.start()

    # Pings all devices and tells them to stop sending data
    for instruction_queue in instruction_queues:
        instruction_queue.put(("ping", []))

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
        elif instruction == "disable_all":
            for instruction_queue in instruction_queues:
                instruction_queue.put(("disable", []))            


def device_write_thread(dev, queue):
    while True:
        instruction, args = queue.get()

        # flush the queue if it's too big
        if queue.qsize() > 10:
            print("flushing queue, size is %d" % queue.qsize())
            while instruction != "disable" and not queue.empty():
                instruction, args = queue.get()

        if instruction == "ping":
            hm.hid_send(dev, hm.make_ping())
        elif instruction == "subscribe":
            uid, delay, params = args
            hm.hid_send(dev, hm.make_subscription_request(hm.uid_to_device_id(uid), params, delay))
        elif instruction == "read":
            uid, params = args
            hm.hid_send(dev, hm.make_device_read(hm.uid_to_device_id(uid), params))
        elif instruction == "write":
            uid, params_and_values = args
            hm.hid_send(dev, hm.make_device_write(hm.uid_to_device_id(uid), params_and_values))
        elif instruction == "disable":
            hm.hid_send(dev, hm.make_disable())
        elif instruction == "heartResp":
            uid = args[0]
            hm.hid_send(dev, hm.make_heartbeat_response())

# global counters for tracking statistics

# number of packets read
ctr = 0
start_time = time.time()
# total time spent parsing received packets
parse_time = 0

def device_read_thread(index, dev, instructionQueue, errorQueue, stateQueue):
    uid = None
    global ctr
    global start_time
    global parse_time
    start_time = time.time()
    while True:
        for packet in hm.hid_blocking_receive_generator(dev):
            ctr += 1
            if ctr % 100 == 0:
                # these are not direct inverses of each other because the second only counts time spent in the loop body
                print("%f reads/second, %f seconds/read" % (ctr/(time.time() - start_time), parse_time/ctr))
            before_time = time.time()
            message_type = packet.getmessageID()
            if message_type == hm.messageTypes["SubscriptionResponse"]:
                params, delay, uid = hm.parse_subscription_response(packet)
                uid_to_index[uid] = index
                stateQueue.put(("device_subscribed", [uid, delay, params]))
            elif message_type == hm.messageTypes["DeviceData"]:
                if uid is not None:
                    params_and_values = hm.parse_device_data(packet, hm.uid_to_device_id(uid))
                    stateQueue.put(("device_values", [uid, params_and_values]))
                else:
                    print("[HIBIKE] Device %s received data before enumerating!!!" % dev)
                    print("Telling it to shut up")
                    hm.hid_send(dev, hm.make_subscription_request(1, [], 0))
            elif message_type == hm.messageTypes["HeartBeatRequest"]:
                if uid is not None:
                    instructionQueue.put(("heartResp", [uid]))
            parse_time += time.time() - before_time



#############
## TESTING ##
#############

if __name__ == "__main__":

    # helper functions so we can spawn threads that try to read/write to hibike_devices periodically
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
        print("waiting for command")
        command, args = stateQueue.get()
        if command == "device_subscribed":
            uid = args[0]
            if uid not in uids:
                uids.add(uid)
                if hm.devices[hm.uid_to_device_id(uid)]["name"] == "ExampleDevice":
                    set_interval_sequence([
                        make_send_write(pipeToChild, uid, [("hazuki", 255), ("sapphire", 0)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 254), ("sapphire", 1)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 253), ("sapphire", 2)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 252), ("sapphire", 3)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 251), ("sapphire", 4)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 250), ("sapphire", 5)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 249), ("sapphire", 6)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 248), ("sapphire", 7)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 247), ("sapphire", 8)]),
                        make_send_write(pipeToChild, uid, [("hazuki", 246), ("sapphire", 9)])
                        ], 0.1)
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
                        make_send_write(pipeToChild, uid, [("duty_cycle", 0)]),
                        make_send_write(pipeToChild, uid, [("duty_cycle", 0.5)]),
                        make_send_write(pipeToChild, uid, [("duty_cycle", 1.0)]),
                        make_send_write(pipeToChild, uid, [("duty_cycle", 0)]),
                        make_send_write(pipeToChild, uid, [("duty_cycle", -0.5)]),
                        make_send_write(pipeToChild, uid, [("duty_cycle", -1.0)]),
                        make_send_write(pipeToChild, uid, [("duty_cycle", 0)])
                        ], 0.75)
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
