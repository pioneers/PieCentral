import socket
import threading
import time
import sys
import selectors
import csv
import runtime_pb2
import ansible_pb2
import notification_pb2
from runtimeUtil import *

UDP_SEND_PORT = 1235
UDP_RECV_PORT = 1236
TCP_PORT = 1234

TCP_HZ = 5.0
# Only for UDPSend Process
PACKAGER_HZ = 5.0
SOCKET_HZ = 5.0


@unique # pylint: disable=invalid-name
class THREAD_NAMES(Enum):
    UDP_PACKAGER = "udpPackager"
    UDP_SENDER = "udpSender"
    UDP_RECEIVER = "udpReceiver"
    UDP_UNPACKAGER = "udpUnpackager"
    TCP_PACKAGER = "tcpPackager"
    TCP_SENDER = "tcpSender"
    TCP_RECEIVER = "tcpReceiver"
    TCP_UNPACKAGER = "tcpUnpackager"


class TwoBuffer():
    """Custom buffer class for handling states.

    Holds two states, one which is updated and one that is sent. A list is used because
    the get and replace methods are atomic operations. Replacing swaps indices of the
    get and put index.

    """

    def __init__(self):
        self.data = [0, 0]
        self.put_index = 0
        self.get_index = 1

    def replace(self, item):
        self.data[self.put_index] = item
        self.put_index = 1 - self.put_index
        self.get_index = 1 - self.get_index

    def get(self):
        return self.data[self.get_index]


class AnsibleHandler():
    """Parent class for UDP Processes that spawns threads

    Initializes generalized instance variables for both UDP sender and receiver, and creates a
    callable method to initialize the two threads for the UDPSend process.
    """

    def __init__(self, packagerName, packagerThread, socketName, socketThread, # pylint: disable=too-many-arguments
                 badThingsQueue, stateQueue, pipe):
        self.packager_fn = packagerThread
        self.socket_fn = socketThread
        self.bad_things_queue = badThingsQueue
        self.state_queue = stateQueue
        self.pipe = pipe
        self.packager_name = packagerName
        self.socket_name = socketName

    def thread_maker(self, thread_target, thread_name):
        thread = threading.Thread(
            target=thread_target,
            name=thread_name,
            args=(
                self,
                self.bad_things_queue,
                self.state_queue,
                self.pipe))
        thread.daemon = True
        return thread

    def start(self):
        packager_thread = self.thread_maker(self.packager_fn, self.packager_name)
        socket_thread = self.thread_maker(self.socket_fn, self.socket_name)
        packager_thread.start()
        socket_thread.start()
        packager_thread.join()
        socket_thread.join()


class UDPSendClass(AnsibleHandler):
    """Class that sends data to Dawn via UDP

    This class extends AnsibleHandler, which handles the constructor and starting threads.
    UDPSend runs in its own process which is started in runtime.py, and spawns two
    threads from this process. One thread is for packaging, and one thread is for sending.
    The packaging thread pulls the current state from SM, and packages the sensor data
    into a proto. It shares the data to the send thread via a TwoBuffer. The send thread
    sends the data over a UDP socket to Dawn on the UDP_SEND_PORT
    """

    def __init__(self, badThingsQueue, stateQueue, pipe):
        self.send_buffer = TwoBuffer()
        packager_name = THREAD_NAMES.UDP_PACKAGER
        sock_send_name = THREAD_NAMES.UDP_SENDER
        stateQueue.put([SM_COMMANDS.SEND_ADDR, [PROCESS_NAMES.UDP_SEND_PROCESS]])
        self.dawn_ip = pipe.recv()[0]
        super().__init__(
            packager_name,
            UDPSendClass.package_data,
            sock_send_name,
            UDPSendClass.udp_sender,
            badThingsQueue,
            stateQueue,
            pipe)

    def package_data(self, bad_things_queue, state_queue, pipe):
        """Function run as a thread that packages data to be sent.

        The robot's current state is received from the StateManager via the pipe and packaged
        by the package function, defined internally. The packaged data is then placed
        back into the TwoBuffer replacing the previous state.
        """
        def package(state):
            """Helper function that packages the current state.

            Parses through the state dictionary in key value pairs, creates a new message in the
            proto for each sensor, and adds corresponding data to each field. Currently only
            supports a single limit_switch switch as the rest of the state is just test fields.
            """
            try:
                proto_message = runtime_pb2.RuntimeData()
                proto_message.robot_state = state['studentCodeState'][0]
                for uid, values in state['hibike'][0]['devices'][0].items():
                    sensor = proto_message.sensor_data.add()
                    sensor.uid = str(uid)
                    sensor.device_type = SENSOR_TYPE[uid >> 72]
                    for param, value in values[0].items():
                        if value[0] is None:
                            continue
                        param_value_pair = sensor.param_value.add()
                        param_value_pair.param = param
                        if isinstance(value[0], bool):
                            param_value_pair.bool_value = value[0]
                        elif isinstance(value[0], float):
                            param_value_pair.float_value = value[0]
                        elif isinstance(value[0], int):
                            param_value_pair.int_value = value[0]
                return proto_message.SerializeToString()
            except Exception as e:
                bad_things_queue.put(
                    BadThing(
                        sys.exc_info(),
                        "UDP packager thread has crashed with error:" +
                        str(e),
                        event=BAD_EVENTS.UDP_SEND_ERROR,
                        printStackTrace=True))
        while True:
            try:
                next_call = time.time()
                state_queue.put([SM_COMMANDS.SEND_ANSIBLE, []])
                raw_state = pipe.recv()
                pack_state = package(raw_state)
                self.send_buffer.replace(pack_state)
                next_call += 1.0 / PACKAGER_HZ
                time.sleep(max(next_call - time.time(), 0))
            except Exception as e:
                bad_things_queue.put(
                    BadThing(
                        sys.exc_info(),
                        "UDP packager thread has crashed with error:" +
                        str(e),
                        event=BAD_EVENTS.UDP_SEND_ERROR,
                        printStackTrace=True))

    def udp_sender(self, bad_things_queue, state_queue, pipe): #pylint: disable=unused-argument
        """Function run as a thread that sends a packaged state from the TwoBuffer

        The current state that has already been packaged is gotten from the
        TwoBuffer, and is sent to Dawn via a UDP socket.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while True:
                try:
                    next_call = time.time()
                    msg = self.send_buffer.get()
                    if msg != 0 and msg is not None and self.dawn_ip is not None:
                        sock.sendto(msg, (self.dawn_ip, UDP_SEND_PORT))
                    next_call += 1.0 / SOCKET_HZ
                    time.sleep(max(next_call - time.time(), 0))
                except Exception as e:
                    bad_things_queue.put(
                        BadThing(
                            sys.exc_info(),
                            "UDP sender thread has crashed with error: " +
                            str(e),
                            event=BAD_EVENTS.UDP_SEND_ERROR,
                            printStackTrace=True))


class UDPRecvClass(AnsibleHandler):
    """Class that receives data from Dawn via UDP

    This class extends AnsibleHandler, which handles the constructor. This class overrides
    the start() function from its parent. UDPRecv runs as its own process which is started
    in runtime.py. No threads are spawned from this process. Receiving from Dawn and unpackaging
    are run in succession. Unpackaged data, which contains gamepad and control_state data
    is sent to SM.
    """

    def __init__(self, badThingsQueue, stateQueue, pipe):
        self.recv_buffer = TwoBuffer()
        packager_name = THREAD_NAMES.UDP_UNPACKAGER
        sock_recv_name = THREAD_NAMES.UDP_RECEIVER
        host = ""  # 0.0.0.0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, UDP_RECV_PORT))
        self.socket.setblocking(False)
        self.curr_addr = None
        self.control_state = None
        self.sm_mapping = {
            ansible_pb2.DawnData.IDLE: SM_COMMANDS.ENTER_IDLE,
            ansible_pb2.DawnData.TELEOP: SM_COMMANDS.ENTER_TELEOP,
            ansible_pb2.DawnData.AUTONOMOUS: SM_COMMANDS.ENTER_AUTO,
            ansible_pb2.DawnData.ESTOP: SM_COMMANDS.EMERGENCY_STOP
        }
        self.team_color_mapping = {
            ansible_pb2.DawnData.BLUE: "blue",
            ansible_pb2.DawnData.GOLD: "yellow",
        }
        super().__init__(
            packager_name,
            UDPRecvClass.unpackage_data,
            sock_recv_name,
            UDPRecvClass.udp_receiver,
            badThingsQueue,
            stateQueue,
            pipe)

    def udp_receiver(self):
        """Function to receive data from Dawn to local TwoBuffer

        Reads from receive port and stores data into TwoBuffer to be shared
        with the unpackager.
        """
        try:
            while True:
                recv_data, addr = self.socket.recvfrom(2048)
        except BlockingIOError:
            self.recv_buffer.replace(recv_data)
            if self.curr_addr is None:
                self.curr_addr = addr
                self.state_queue.put([SM_COMMANDS.SET_ADDR, [addr]])

    def unpackage_data(self):
        """Unpackages data from proto and sends to stateManager on the SM stateQueue

        """
        def unpackage(data):
            """Function that takes a packaged proto and unpackages the item

            Parses through the python pseudo-class created by the protobuf and stores it into a
            dictionary. All of the axes data and the button data, enumerates each value to follow
            a mapping shared by dawn, and stores it in the dictionary with the gamepad index
            as a key.

            Student code status is also stored in this dictionary. This dictionary is added to
            the overall state through the update method implemented in state manager.
            """
            unpackaged_data = {}
            received_proto = ansible_pb2.DawnData()
            received_proto.ParseFromString(data)
            new_state = received_proto.student_code_status
            unpackaged_data["student_code_status"] = [new_state, time.time()]
            if self.pipe.poll():
                self.control_state = self.pipe.recv()
            if self.control_state is None or new_state != self.control_state:
                self.control_state = received_proto.student_code_status
                sm_state_command = self.sm_mapping[new_state]
                self.state_queue.put([sm_state_command, []])
            all_gamepad_dict = {}
            for gamepad in received_proto.gamepads:
                gamepad_dict = {}
                gamepad_dict["axes"] = dict(enumerate(gamepad.axes))
                gamepad_dict["buttons"] = dict(enumerate(gamepad.buttons))
                all_gamepad_dict[gamepad.index] = gamepad_dict
            unpackaged_data["gamepads"] = [all_gamepad_dict, time.time()]
            if received_proto.team_color != ansible_pb2.DawnData.NONE:
                self.state_queue.put([SM_COMMANDS.SET_TEAM,
                                      [self.team_color_mapping[received_proto.team_color]]])
            return unpackaged_data

        unpackaged_data = unpackage(self.recv_buffer.get())
        self.state_queue.put([SM_COMMANDS.RECV_ANSIBLE, [unpackaged_data]])

    def start(self):
        """Overwrites start in parent class so it doesn't run in two threads

        Creates a selector to block if the socket hasn't received any data since
        we set the socket to nonblocking. If it receives data, it then calls the
        udp_receiver function to get the newest packet. Then it calls the unpackage_data
        function to unpackage and send to the stateQueue.
        """
        sel = selectors.DefaultSelector()
        sel.register(self.socket, selectors.EVENT_READ)

        try:
            while True:
                sel.select()
                self.udp_receiver()
                self.unpackage_data()
        except Exception as e:
            self.bad_things_queue.put(
                BadThing(
                    sys.exc_info(),
                    "UDP receiver thread has crashed with error: " +
                    str(e),
                    event=BAD_EVENTS.UDP_RECV_ERROR,
                    printStackTrace=True))


class TCPClass(AnsibleHandler):
    """Class that communicates with Dawn via TCP connection

    This class extends AnsibleHandler, which handles the constructor and start() method
    This class runs as its own process, started in runtime.py. The process spawns two
    threads, one for sending and one for receiving. Both TCPSend and TCPRecv communicate with
    both SM and Dawn. Runtime is the client of the TCP connection, so runtime binds to the
    server created by Dawn on construction. On first connection, runtime sends all peripheral
    namings to Dawn.
    """

    def __init__(self, badThingsQueue, stateQueue, pipe):
        self.send_buffer = TwoBuffer()
        self.recv_buffer = TwoBuffer()
        send_name = THREAD_NAMES.TCP_SENDER
        recv_name = THREAD_NAMES.TCP_RECEIVER
        super().__init__(
            send_name,
            TCPClass.sender,
            recv_name,
            TCPClass.receiver,
            badThingsQueue,
            stateQueue,
            pipe)

        stateQueue.put([SM_COMMANDS.SEND_ADDR, [PROCESS_NAMES.TCP_PROCESS]])
        self.dawn_ip = pipe.recv()[0]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.dawn_ip, TCP_PORT))

        proto_message = notification_pb2.Notification()
        proto_message.header = notification_pb2.Notification.SENSOR_MAPPING
        with open('namedPeripherals.csv', 'r') as mapping_file:
            sensor_mappings = csv.reader(mapping_file)
            for row in sensor_mappings:
                pair = proto_message.sensor_mapping.add()
                pair.device_student_name = row[0]
                pair.device_uid = row[1]
        self.sock.sendall(proto_message.SerializeToString())

    def sender(self, bad_things_queue, state_queue, pipe): # pylint: disable=unused-argument
        """Function run in an individual thread that sends data to Dawn via TCP

        The sender will send either console logging or confirmation that runtime is ready
        for student code upload.
        """

        def package_message(data):
            try:
                proto_message = notification_pb2.Notification()
                proto_message.header = notification_pb2.Notification.CONSOLE_LOGGING
                proto_message.console_output = data
                return proto_message.SerializeToString()
            except Exception as e:
                bad_things_queue.put(
                    BadThing(
                        sys.exc_info(),
                        "TCP packager crashed with error: " +
                        str(e),
                        event=BAD_EVENTS.TCP_ERROR,
                        printStackTrace=True))

        def package_confirm(confirm):
            try:
                proto_message = notification_pb2.Notification()
                if confirm:
                    proto_message.header = notification_pb2.Notification.STUDENT_RECEIVED
                else:
                    proto_message.header = notification_pb2.Notification.STUDENT_NOT_RECEIVED
                return proto_message.SerializeToString()
            except Exception as e:
                bad_things_queue.put(
                    BadThing(
                        sys.exc_info(),
                        "TCP packager crashed with error: " +
                        str(e),
                        event=BAD_EVENTS.TCP_ERROR,
                        printStackTrace=True))
        while True:
            try:
                raw_message = pipe.recv()
                next_call = time.time()
                next_call += 1.0 / TCP_HZ
                data = raw_message[1]
                if raw_message[0] == ANSIBLE_COMMANDS.STUDENT_UPLOAD:
                    packed_msg = package_confirm(data)
                elif raw_message[0] == ANSIBLE_COMMANDS.CONSOLE:
                    packed_msg = package_message(data)
                else:
                    continue
                if packed_msg is not None:
                    self.sock.sendall(packed_msg)
                # Sleep for throttling thread
                time.sleep(max(next_call - time.time(), 0))
            except Exception as e:
                bad_things_queue.put(BadThing(sys.exc_info(),
                                              "TCP sender crashed with error: " +
                                              str(e),
                                              event=BAD_EVENTS.TCP_ERROR,
                                              printStackTrace=True))

    def receiver(self, bad_things_queue, state_queue, pipe): # pylint: disable=unused-argument
        """Function run in its own thread which receives data from Dawn

        The receiver can receive a command that Dawn is about to upload student Code.
        This message is passed along to SM to ensure all appropriate processes are kiled.

        The receiver detects disconnection from Dawn and restarts all Ansible processes
        by sending a BadThing to runtime.py
        """

        def unpackage(data):
            received_proto = notification_pb2.Notification()
            received_proto.ParseFromString(data)
            return received_proto
        try:
            while True:
                recv_data, _ = self.sock.recvfrom(2048)
                if recv_data == b'':
                    bad_things_queue.put(
                        BadThing(
                            sys.exc_info(),
                            "restarting Ansible Processes due to disconnection",
                            event=BAD_EVENTS.DAWN_DISCONNECTED,
                            printStackTrace=False))
                    break
                unpackaged_data = unpackage(recv_data) # pylint: disable=unused-variable
                state_queue.put([SM_COMMANDS.STUDENT_UPLOAD, []])
        except ConnectionResetError:
            bad_things_queue.put(
                BadThing(
                    sys.exc_info(),
                    "restarting Ansible Processes due to disconnection",
                    event=BAD_EVENTS.DAWN_DISCONNECTED,
                    printStackTrace=False))
        except Exception as e:
            bad_things_queue.put(
                BadThing(
                    sys.exc_info(),
                    "TCP receiver crashed with error: " +
                    str(e),
                    event=BAD_EVENTS.TCP_ERROR,
                    printStackTrace=True))
