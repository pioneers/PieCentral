"""
The main Hibike process.
"""
from collections import namedtuple
import glob
import multiprocessing
import os
import queue
import threading
import time

# pylint: disable=import-error
import hibike_message as hm
import serial

__all__ = ["hibike_process"]


# .04 milliseconds sleep is the same frequency we subscribe to devices at
BATCH_SLEEP_TIME = .04
# Time in seconds to wait until reading from a potential sensor
IDENTIFY_TIMEOUT = 1


def get_working_serial_ports():
    """
    Scan for open COM ports.

    Returns:
        A list of serial port objects (`serial.Serial`) and port names.
    """
    # Last command is included so that it's compatible with OS X Sierra
    # Note: If you are running OS X Sierra, do not access the directory through vagrant ssh
    # Instead access it through Volumes/vagrant/PieCentral
    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*") + glob.glob("/dev/tty.usbmodem*")
    try:
        virtual_device_config_file = os.path.join(os.path.dirname(__file__), "virtual_devices.txt")
        ports.extend(open(virtual_device_config_file, "r").read().split())
    except IOError:
        pass

    serials = []
    port_names = []
    for port in ports:
        try:
            serials.append(serial.Serial(port, 115200))
            port_names.append(port)
        # this implementation ensures that as long as the cannot open serial port error occurs
        # while opening the serial port, a print will appear, but
        # the rest of the ports will go on.
        except serial.serialutil.SerialException:
            print("Cannot Open Serial Port: " + str(port))
    return serials, port_names


def identify_smart_sensors(serial_conns):
    """
    Given a list of serial port connections, figure out which
    contain smart sensors.

    Returns:
        A map of serial port names to UIDs.
    """
    def recv_subscription_requests(conn, uid_queue, stop_event):
        """
        Place received subscription request UIDs from CONN into UID_QUEUE,
        stopping when STOP_EVENT is set.
        """
        for packet in hm.blocking_read_generator(conn, stop_event):
            msg_type = packet.get_message_id()
            if msg_type == hm.MESSAGE_TYPES["SubscriptionResponse"]:
                _, _, uid = hm.parse_subscription_response(packet)
                uid_queue.put(uid)
    device_map = {}
    thread_list = []
    event_list = []
    read_queues = []

    for conn in serial_conns:
        old_timeout = conn.write_timeout
        conn.write_timeout = IDENTIFY_TIMEOUT
        try:
            hm.send(conn, hm.make_ping())
        except serial.SerialTimeoutException:
            continue
        finally:
            conn.write_timeout = old_timeout
        curr_queue = queue.Queue()
        curr_event = threading.Event()
        thread_list.append(threading.Thread(target=recv_subscription_requests,
                                            args=(conn, curr_queue, curr_event)))
        read_queues.append(curr_queue)
        event_list.append(curr_event)
    for thread in thread_list:
        thread.start()
    for (index, reader) in enumerate(read_queues):
        try:
            uid = reader.get(block=True, timeout=IDENTIFY_TIMEOUT)
            device_map[serial_conns[index].name] = uid
        except queue.Empty:
            pass
    for (event, thread) in zip(event_list, thread_list):
        event.set()
        thread.join()
    return device_map

# pylint: disable=too-many-branches, too-many-locals
# pylint: disable=too-many-arguments, unused-argument
def hibike_process(bad_things_queue, state_queue, pipe_from_child):
    """
    Run the main hibike processs.
    """
    serials, serial_names = get_working_serial_ports()
    smart_sensors = identify_smart_sensors(serials)
    devices = {}

    batched_data = {}

    for (ser, uid) in smart_sensors.items():
        index = serial_names.index(ser)
        serial_port = serials[index]
        pack = namedtuple("Threadpack", ["read_thread", "write_thread",
                                         "write_queue"])
        pack.write_queue = queue.Queue()
        pack.write_thread = threading.Thread(target=device_write_thread,
                                             args=(serial_port, pack.write_queue))
        pack.read_thread = threading.Thread(target=device_read_thread,
                                            args=(uid, serial_port, pack.write_queue, None,
                                                  state_queue, batched_data))
        pack.write_thread.start()
        pack.read_thread.start()
        devices[uid] = pack

    batch_thread = threading.Thread(target=batch_data, args=(batched_data, state_queue))
    batch_thread.start()

    # Pings all devices and tells them to stop sending data
    for pack in devices.values():
        pack.write_queue.put(("ping", []))
        pack.write_queue.put(("subscribe", [1, 0, []]))

    # the main thread reads instructions from statemanager and
    # forwards them to the appropriate device write threads
    while True:
        instruction, args = pipe_from_child.recv()
        if instruction == "enumerate_all":
            for pack in devices.values():
                pack.write_queue.put(("ping", []))
        elif instruction == "subscribe_device":
            uid = args[0]
            if uid in devices:
                devices[uid].write_queue.put(("subscribe", args))
        elif instruction == "write_params":
            uid = args[0]
            if uid in devices:
                devices[uid].write_queue.put(("write", args))
        elif instruction == "read_params":
            uid = args[0]
            if uid in devices:
                devices[uid].write_queue.put(("read", args))
        elif instruction == "disable_all":
            for pack in devices.values():
                pack.write_queue.put(("disable", []))


def device_write_thread(ser, instr_queue):
    """
    Send packets to SER based on instructions from INSTR_QUEUE.
    """
    while True:
        instruction, args = instr_queue.get()

        if instruction == "ping":
            hm.send(ser, hm.make_ping())
        elif instruction == "subscribe":
            uid, delay, params = args
            hm.send(ser, hm.make_subscription_request(hm.uid_to_device_id(uid), params, delay))
        elif instruction == "read":
            uid, params = args
            hm.send(ser, hm.make_device_read(hm.uid_to_device_id(uid), params))
        elif instruction == "write":
            uid, params_and_values = args
            hm.send(ser, hm.make_device_write(hm.uid_to_device_id(uid), params_and_values))
        elif instruction == "disable":
            hm.send(ser, hm.make_disable())
        elif instruction == "heartResp":
            uid = args[0]
            hm.send(ser, hm.make_heartbeat_response())


def device_read_thread(uid, ser, instruction_queue, error_queue, state_queue, batched_data):
    """
    Read packets from SER and update queues and BATCHED_DATA accordingly.
    """
    while True:
        for packet in hm.blocking_read_generator(ser):
            message_type = packet.get_message_id()
            if message_type == hm.MESSAGE_TYPES["SubscriptionResponse"]:
                params, delay, uid = hm.parse_subscription_response(packet)
                state_queue.put(("device_subscribed", [uid, delay, params]))
            elif message_type == hm.MESSAGE_TYPES["DeviceData"]:
                params_and_values = hm.parse_device_data(packet, hm.uid_to_device_id(uid))
                batched_data[uid] = params_and_values
            elif message_type == hm.MESSAGE_TYPES["HeartBeatRequest"]:
                instruction_queue.put(("heartResp", [uid]))

def batch_data(data, state_queue):
    """
    Write out DATA to STATE_QUEUE periodically.
    """
    while True:
        time.sleep(BATCH_SLEEP_TIME)
        state_queue.put(("device_values", [data]))


#############
## TESTING ##
#############
# pylint: disable=invalid-name
if __name__ == "__main__":

    # helper functions so we can spawn threads that try to read/write to hibike_devices periodically
    def set_interval_sequence(functions, sec):
        """
        Create a thread that executes FUNCTIONS after SEC seconds.
        """
        def func_wrapper():
            """
            Execute the next function in FUNCTIONS after SEC seconds.

            Cycles through all functions.
            """
            set_interval_sequence(functions[1:] + functions[:1], sec)
            functions[0]()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def make_send_write(pipe_to_child, uid, params_and_values):
        """
        Create a function that sends UID and PARAMS_AND_VALUES
        to PIPE_TO_CHILD.
        """
        def helper():
            """
            Helper function.
            """
            pipe_to_child.send(["write_params", [uid, params_and_values]])
        return helper

    to_child, from_child = multiprocessing.Pipe()
    main_error_queue = multiprocessing.Queue()
    main_state_queue = multiprocessing.Queue()
    newProcess = multiprocessing.Process(target=hibike_process,
                                         name="hibike_sim",
                                         args=[main_error_queue, main_state_queue, from_child])
    newProcess.daemon = True
    newProcess.start()
    to_child.send(["enumerate_all", []])
    uids = set()
    while True:
        print("waiting for command")
        command, main_args = main_state_queue.get()
        if command == "device_subscribed":
            dev_uid = main_args[0]
            if dev_uid not in uids:
                uids.add(dev_uid)
                if hm.DEVICES[hm.uid_to_device_id(dev_uid)]["name"] == "TeamFlag":
                    set_interval_sequence([
                        make_send_write(to_child, dev_uid,
                                        [("led1", 1), ("led2", 0), ("led3", 0),
                                         ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(to_child, dev_uid,
                                        [("led1", 0), ("led2", 1), ("led3", 0),
                                         ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(to_child, dev_uid,
                                        [("led1", 0), ("led2", 0), ("led3", 1),
                                         ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(to_child, dev_uid,
                                        [("led1", 0), ("led2", 0), ("led3", 0),
                                         ("led4", 1), ("blue", 0), ("yellow", 0)]),
                        make_send_write(to_child, dev_uid,
                                        [("led1", 0), ("led2", 0), ("led3", 0),
                                         ("led4", 0), ("blue", 0), ("yellow", 1)]),
                        make_send_write(to_child, dev_uid,
                                        [("led1", 0), ("led2", 0), ("led3", 0),
                                         ("led4", 0), ("blue", 1), ("yellow", 0)])
                        ], 0.1)
                elif hm.DEVICES[hm.uid_to_device_id(dev_uid)]["name"] == "YogiBear":
                    set_interval_sequence([
                        make_send_write(to_child, dev_uid, [("duty_cycle", 0)]),
                        make_send_write(to_child, dev_uid, [("duty_cycle", 0.5)]),
                        make_send_write(to_child, dev_uid, [("duty_cycle", 1.0)]),
                        make_send_write(to_child, dev_uid, [("duty_cycle", 0)]),
                        make_send_write(to_child, dev_uid, [("duty_cycle", -0.5)]),
                        make_send_write(to_child, dev_uid, [("duty_cycle", -1.0)]),
                        make_send_write(to_child, dev_uid, [("duty_cycle", 0)])
                        ], 0.75)
                elif hm.DEVICES[hm.uid_to_device_id(dev_uid)]["name"] == "ServoControl":
                    set_interval_sequence([
                        make_send_write(to_child, dev_uid,
                                        [("servo0", 1), ("enable0", False),
                                         ("servo1", 21), ("enable1", True),
                                         ("servo2", 30), ("enable2", True),
                                         ("servo3", 8), ("enable3", True)]),
                        make_send_write(to_child, dev_uid,
                                        [("servo0", 5), ("enable0", False),
                                         ("servo1", 5), ("enable1", True),
                                         ("servo2", 5), ("enable2", True),
                                         ("servo3", 5), ("enable3", False)]),
                        make_send_write(to_child, dev_uid,
                                        [("servo0", 1), ("enable0", True),
                                         ("servo1", 26), ("enable1", True),
                                         ("servo2", 30), ("enable2", False),
                                         ("servo3", 17), ("enable3", True)]),
                        make_send_write(to_child, dev_uid,
                                        [("servo0", 13), ("enable0", False),
                                         ("servo1", 7), ("enable1", False),
                                         ("servo2", 24), ("enable2", True),
                                         ("servo3", 10), ("enable3", True)]),
                        make_send_write(to_child, dev_uid,
                                        [("servo0", 27), ("enable0", True),
                                         ("servo1", 2), ("enable1", False),
                                         ("servo2", 3), ("enable2", False),
                                         ("servo3", 14), ("enable3", False)]),
                        make_send_write(to_child, dev_uid,
                                        [("servo0", 20), ("enable0", True),
                                         ("servo1", 12), ("enable1", False),
                                         ("servo2", 20), ("enable2", False),
                                         ("servo3", 29), ("enable3", True)]),
                        ], 1)
                parameters = []
                for param in hm.DEVICES[hm.uid_to_device_id(dev_uid)]["params"]:
                    parameters.append(param["name"])
                to_child.send(["subscribe_device", [dev_uid, 10, parameters]])
        elif command == "device_values":
            print("%10.2f, %s" % (time.time(), str(main_args)))
