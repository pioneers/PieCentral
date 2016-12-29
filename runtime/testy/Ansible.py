import socket
import threading
import time
import sys
import selectors
import runtime_pb2
import ansible_pb2

from runtimeUtil import *

@unique
class THREAD_NAMES(Enum):
    UDP_PACKAGER        = "udpPackager"
    UDP_SENDER          = "udpSender"
    UDP_RECEIVER        = "udpReceiver"
    UDP_UNPACKAGER      = "udpUnpackager"

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
    SEND_PORT = 1235
    packagerHZ = 20.0
    socketHZ = 20.0

    def __init__(self, badThingsQueue, stateQueue, pipe):
        self.sendBuffer = TwoBuffer()
        packagerName = THREAD_NAMES.UDP_PACKAGER
        sockSendName = THREAD_NAMES.UDP_SENDER
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
                for devID, devVal in state.items():
                    if (devID == 'studentCodeState'):
                        proto_message.robot_state = devVal[0] #check if we are dealing with sensor data or student code state
                    elif devID == 'limit_switch':
                        test_sensor = proto_message.sensor_data.add() 
                        test_sensor.device_name = devID
                        test_sensor.device_type = devVal[0][0]
                        test_sensor.value = devVal[0][1]
                        test_sensor.uid = devVal[0][2]
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
                nextCall += 1.0/self.packagerHZ
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
        host = '192.168.128.30' #TODO: Make this not hard coded
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            while True: 
                try:
                    nextCall = time.time()
                    msg = self.sendBuffer.get()
                    if msg != 0 and msg is not None: 
                        s.sendto(msg, (host, UDPSendClass.SEND_PORT))
                    nextCall += 1.0/self.socketHZ
                    time.sleep(max(nextCall - time.time(), 0))
                except Exception:
                    badThingsQueue.put(BadThing(sys.exc_info(), 
                    "UDP sender thread has crashed with error: " + str(e),  
                    event = BAD_EVENTS.UDP_SEND_ERROR, 
                    printStackTrace = True))

class UDPRecvClass(AnsibleHandler):
    RECV_PORT = 1236

    def __init__(self, badThingsQueue, stateQueue, pipe):
        self.recvBuffer = TwoBuffer()        
        packName = THREAD_NAMES.UDP_UNPACKAGER
        sockRecvName = THREAD_NAMES.UDP_RECEIVER
        host = "" #0.0.0.0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, UDPRecvClass.RECV_PORT))
        self.socket.setblocking(False)
        super().__init__(packName, UDPRecvClass.unpackageData, sockRecvName,
                         UDPRecvClass.udpReceiver, badThingsQueue, stateQueue, pipe)

    def udpReceiver(self):
        """Function to receive data from Dawn to local TwoBuffer

        Reads from receive port and stores data into TwoBuffer to be shared
        with the unpackager.
        """
        try:
            while True:
                recv_data = self.socket.recv(2048)
        except BlockingIOError:
            self.recvBuffer.replace(recv_data)

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
            unpackaged_data["student_code_status"] = [received_proto.student_code_status, time.time()]
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
                nextCall = time.time()
                event = sel.select()
                self.udpReceiver()
                self.unpackageData()
                try:
                    time.sleep(nextCall - time.time())
                except ValueError:
                    continue
        except Exception as e:
            self.badThingsQueue.put(BadThing(sys.exc_info(),
            "UDP receiver thread has crashed with error: " + str(e),
            event = BAD_EVENTS.UDP_RECV_ERROR,
            printStackTrace = True))
