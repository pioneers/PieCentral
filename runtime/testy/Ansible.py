import socket
import threading
import time
import sys
import selectors
import runtime_pb2
import ansible_pb2
import notification_pb2
import csv
from runtimeUtil import *

UDP_SEND_PORT = 1235
UDP_RECV_PORT = 1236
TCP_PORT = 1234

TCP_HZ = 5.0
#Only for UDPSend Process
packagerHZ = 5.0
socketHZ = 5.0

@unique
class THREAD_NAMES(Enum):
    UDP_PACKAGER        = "udpPackager"
    UDP_SENDER          = "udpSender"
    UDP_RECEIVER        = "udpReceiver"
    UDP_UNPACKAGER      = "udpUnpackager"
    TCP_PACKAGER        = "tcpPackager"
    TCP_SENDER          = "tcpSender"
    TCP_RECEIVER        = "tcpReceiver"
    TCP_UNPACKAGER      = "tcpUnpackager"

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

    Initializes generalized instance variables for both UDP sender and receiver, and creates a callable
    method to initialize the two threads per UDP process and start them. 
    """
    def __init__(self, packagerName, packagerThread, socketName, socketThread,
                 badThingsQueue, stateQueue, pipe):
        self.packagerFunc = packagerThread
        self.socketFunc = socketThread
        self.badThingsQueue = badThingsQueue
        self.stateQueue = stateQueue
        self.pipe = pipe
        self.packagerName = packagerName
        self.socketName = socketName

    def threadMaker(self, threadTarget, threadName):
        thread = threading.Thread(target=threadTarget,
                                  name=threadName,
                                  args=(self, self.badThingsQueue, self.stateQueue, self.pipe))
        thread.daemon = True
        return thread

    def start(self):
        packagerThread = self.threadMaker(self.packagerFunc, self.packagerName)
        socketThread = self.threadMaker(self.socketFunc, self.socketName)
        packagerThread.start()
        socketThread.start()
        packagerThread.join()
        socketThread.join()

class UDPSendClass(AnsibleHandler):

    def __init__(self, badThingsQueue, stateQueue, pipe):
        self.sendBuffer = TwoBuffer()
        packagerName = THREAD_NAMES.UDP_PACKAGER
        sockSendName = THREAD_NAMES.UDP_SENDER
        stateQueue.put([SM_COMMANDS.SEND_ADDR, [PROCESS_NAMES.UDP_SEND_PROCESS]])
        self.dawn_ip = pipe.recv()[0]
        super().__init__(packagerName, UDPSendClass.packageData, sockSendName,
                         UDPSendClass.udpSender, badThingsQueue, stateQueue, pipe)

    def packageData(self, badThingsQueue, stateQueue, pipe):
        """Function run as a thread that packages data to be sent.

        The robot's current state is received from the StateManager via the pipe and packaged 
        by the package function, defined internally. The packaged data is then placed 
        back into the TwoBuffer replacing the previous state.
        """
        def package(state):
            """Helper function that packages the current state.

            Parses through the state dictionary in key value pairs, creates a new message in the proto
            for each sensor, and adds corresponding data to each field. Currently only supports a single limit_switch
            switch as the rest of the state is just test fields.
            """
            try:
                proto_message = runtime_pb2.RuntimeData()
                proto_message.robot_state = state['studentCodeState'][0]
                for uid, values in state['hibike'][0]['devices'][0].items():
                    sensor = proto_message.sensor_data.add()
                    sensor.uid = str(uid)
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
                badThingsQueue.put(BadThing(sys.exc_info(),
                    "UDP packager thread has crashed with error:" + str(e),
                    event = BAD_EVENTS.UDP_SEND_ERROR,
                    printStackTrace = True))
        while True:
            try:
                nextCall = time.time()
                stateQueue.put([SM_COMMANDS.SEND_ANSIBLE, []])
                rawState = pipe.recv()
                packState = package(rawState)
                self.sendBuffer.replace(packState)
                nextCall += 1.0/packagerHZ
                time.sleep(max(nextCall - time.time(), 0))
            except Exception as e:
                badThingsQueue.put(BadThing(sys.exc_info(), 
                    "UDP packager thread has crashed with error:" + str(e),
                    event = BAD_EVENTS.UDP_SEND_ERROR, 
                    printStackTrace = True))

    def udpSender(self, badThingsQueue, stateQueue, pipe):
        """Function run as a thread that sends a packaged state from the TwoBuffer
        
        The current state that has already been packaged is gotten from the 
        TwoBuffer, and is sent to Dawn via a UDP socket.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            while True: 
                try:
                    nextCall = time.time()
                    msg = self.sendBuffer.get()
                    if msg != 0 and msg is not None and self.dawn_ip is not None:
                        s.sendto(msg, (self.dawn_ip, UDP_SEND_PORT))
                    nextCall += 1.0/socketHZ
                    time.sleep(max(nextCall - time.time(), 0))
                except Exception as e:
                    badThingsQueue.put(BadThing(sys.exc_info(), 
                    "UDP sender thread has crashed with error: " + str(e),  
                    event = BAD_EVENTS.UDP_SEND_ERROR, 
                    printStackTrace = True))

class UDPRecvClass(AnsibleHandler):    
    def __init__(self, badThingsQueue, stateQueue, pipe):
        self.recvBuffer = TwoBuffer()        
        packName = THREAD_NAMES.UDP_UNPACKAGER
        sockRecvName = THREAD_NAMES.UDP_RECEIVER
        host = "" #0.0.0.0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, UDP_RECV_PORT))
        self.socket.setblocking(False)
        self.curr_addr = None
        self.control_state = None
        self.sm_mapping = {
            ansible_pb2.DawnData.IDLE       : SM_COMMANDS.ENTER_IDLE,
            ansible_pb2.DawnData.TELEOP     : SM_COMMANDS.ENTER_TELEOP,
            ansible_pb2.DawnData.AUTONOMOUS : SM_COMMANDS.ENTER_AUTO,
            ansible_pb2.DawnData.ESTOP      : SM_COMMANDS.EMERGENCY_STOP
        }
        super().__init__(packName, UDPRecvClass.unpackageData, sockRecvName,
                         UDPRecvClass.udpReceiver, badThingsQueue, stateQueue, pipe)

    def udpReceiver(self):
        """Function to receive data from Dawn to local TwoBuffer

        Reads from receive port and stores data into TwoBuffer to be shared
        with the unpackager.
        """
        try:
            while True:
                recv_data, addr = self.socket.recvfrom(2048)
        except BlockingIOError:
            self.recvBuffer.replace(recv_data)
            if self.curr_addr is None:
                self.curr_addr = addr
                self.stateQueue.put([SM_COMMANDS.SET_ADDR, [addr]])

    def unpackageData(self):
        """Unpackages data from proto and sends to stateManager on the SM stateQueue

        """
        def unpackage(data):
            """Function that takes a packaged proto and unpackages the item

            Parses through the python pseudo-class created by the protobuf and stores it into a dictionary.
            All of the axes data and the button data, enumerates each value to follow a mapping shared by dawn,
            and stores it in the dictionary with the gamepad index as a key.

            student code status is also stored in this dictionary. This dictionary is added to the overall state
            through the update method implemented in state manager.
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
                self.stateQueue.put([sm_state_command, []])
            all_gamepad_dict = {}
            for gamepad in received_proto.gamepads:
                gamepad_dict = {}
                gamepad_dict["axes"] = dict(enumerate(gamepad.axes))
                gamepad_dict["buttons"] = dict(enumerate(gamepad.buttons))
                all_gamepad_dict[gamepad.index] = gamepad_dict
            unpackaged_data["gamepads"] = [all_gamepad_dict, time.time()]
            return unpackaged_data

        unpackagedData = unpackage(self.recvBuffer.get())
        self.stateQueue.put([SM_COMMANDS.RECV_ANSIBLE, [unpackagedData]])

    def start(self):
        """Overwrites start in parent class so it doesn't run in two threads

        Creates a selector to block if the socket hasn't received any data since
        we set the socket to nonblocking. If it receives data, it then calls the
        udpReceiver function to get the newest packet. Then it calls the unpackageData
        function to unpackage and send to the stateQueue. 
        """
        sel = selectors.DefaultSelector()
        sel.register(self.socket, selectors.EVENT_READ)

        try:
            while True:
                event = sel.select()
                self.udpReceiver()
                self.unpackageData()
        except Exception as e:
            self.badThingsQueue.put(BadThing(sys.exc_info(),
            "UDP receiver thread has crashed with error: " + str(e),
            event = BAD_EVENTS.UDP_RECV_ERROR,
            printStackTrace = True))

class TCPClass(AnsibleHandler):

    def __init__(self, badThingsQueue, stateQueue, pipe):
        self.sendBuffer = TwoBuffer()
        self.recvBuffer = TwoBuffer()
        sendName = THREAD_NAMES.TCP_SENDER
        recvName = THREAD_NAMES.TCP_RECEIVER
        super().__init__(sendName, TCPClass.sender, recvName, TCPClass.receiver, badThingsQueue, stateQueue, pipe)

        stateQueue.put([SM_COMMANDS.SEND_ADDR, [PROCESS_NAMES.TCP_PROCESS]])
        self.dawn_ip = pipe.recv()[0]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.dawn_ip, TCP_PORT))

        proto_message = notification_pb2.Notification()
        proto_message.header = notification_pb2.Notification.SENSOR_MAPPING
        with open('namedPeripherals.csv', 'r') as f:
            sensorMappings = csv.reader(f)
            for row in sensorMappings:
                pair = proto_message.sensor_mapping.add()
                pair.device_student_name = row[0]
                pair.device_uid = row[1]
        self.sock.sendall(proto_message.SerializeToString())

    def sender(self, badThingsQueue, stateQueue, pipe):
        def packageMessage(data):
            try:
                proto_message = notification_pb2.Notification()
                proto_message.header = notification_pb2.Notification.CONSOLE_LOGGING
                proto_message.console_output = data
                return proto_message.SerializeToString()
            except Exception as e:
                badThingsQueue.put(BadThing(sys.exc_info(), 
                    "TCP packager crashed with error: " + str(e),
                    event = BAD_EVENTS.TCP_ERROR,
                    printStackTrace = True))
        def packageConfirm(confirm):
            try:
                proto_message = notification_pb2.Notification()
                if confirm:
                    proto_message.header = notification_pb2.Notification.STUDENT_RECEIVED
                else:
                    proto_message.header = notification_pb2.Notification.STUDENT_NOT_RECEIVED
                return proto_message.SerializeToString()
            except Exception as e:
                badThingsQueue.put(BadThing(sys.exc_info(), 
                    "TCP packager crashed with error: " + str(e),
                    event = BAD_EVENTS.TCP_ERROR,
                    printStackTrace = True))
        while True:
            try:
                rawMessage = pipe.recv()
                nextCall = time.time()
                nextCall += 1.0/TCP_HZ
                data = rawMessage[1]
                if rawMessage[0] == ANSIBLE_COMMANDS.STUDENT_UPLOAD:
                    packedMsg = packageConfirm(data)
                elif rawMessage[0] == ANSIBLE_COMMANDS.CONSOLE:
                    packedMsg = packageMessage(data)
                else:
                    continue
                if packedMsg is not None:
                    self.sock.sendall(packedMsg)
                #Sleep for throttling thread
                time.sleep(max(nextCall - time.time(), 0))
            except Exception as e:
                badThingsQueue.put(BadThing(sys.exc_info(), 
                    "TCP sender crashed with error: " + str(e),
                    event = BAD_EVENTS.TCP_ERROR,
                    printStackTrace = True))

    def receiver(self, badThingsQueue, stateQueue, pipe):
        def unpackage(data):
            received_proto = notification_pb2.Notification()
            received_proto.ParseFromString(data)
            return received_proto
        try:
            while True:
                recv_data, addr = self.sock.recvfrom(2048)
                if recv_data == b'':
                    badThingsQueue.put(BadThing(sys.exc_info(),
                    "restarting Ansible Processes due to disconnection",
                    event = BAD_EVENTS.DAWN_DISCONNECTED,
                    printStackTrace = False))
                    break
                unpackagedData = unpackage(recv_data)
                stateQueue.put([SM_COMMANDS.STUDENT_UPLOAD, []])
        except ConnectionResetError:
            badThingsQueue.put(BadThing(sys.exc_info(),
                    "restarting Ansible Processes due to disconnection",
                    event = BAD_EVENTS.DAWN_DISCONNECTED,
                    printStackTrace = False))
        except Exception as e:
                badThingsQueue.put(BadThing(sys.exc_info(), 
                    "TCP receiver crashed with error: " + str(e),
                    event = BAD_EVENTS.TCP_ERROR,
                    printStackTrace = True))
