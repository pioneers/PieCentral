import socket
import threading
import time
import sys
import selectors

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

            Currently this function converts the input into bytes. This will
            eventually be implemented to package the rawState into protos.
            """
            s = "TEST" 
            b = bytearray(map(ord, s))
            return b 

        while True:
            try:
                nextCall = time.time()
                stateQueue.put([SM_COMMANDS.SEND_ANSIBLE, []])
                rawState = pipe.recv()
                packState = package(rawState)
                self.sendBuffer.replace(packState)
                nextCall += 1.0/self.packagerHZ
                if (nextCall > time.time()):
                    time.sleep(nextCall - time.time())
            except Exception:
                badThingsQueue.put(BadThing(sys.exc_info(), 
                    "UDP packager thread has crashed with error:",  
                    event = BAD_EVENTS.UDP_SEND_ERROR, 
                    printStackTrace = True))

    def udpSender(self, badThingsQueue, stateQueue, pipe):
        """Function run as a thread that sends a packaged state from the TwoBuffer
        
        The current state that has already been packaged is gotten from the 
        TwoBuffer, and is sent to Dawn via a UDP socket.
        """
        host = '127.0.0.1' #TODO: determine host in runtime-dawn comm
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            while True: 
                try:
                    nextCall = time.time()
                    msg = self.sendBuffer.get()
                    if msg != 0: 
                        s.sendto(msg, (host, UDPSendClass.SEND_PORT))
                    nextCall += 1.0/self.socketHZ
                    if (nextCall > time.time()):
                        time.sleep(nextCall - time.time())
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
        host = '127.0.0.1' #TODO: determine host between dawn-runtime comm
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

        Sending data from dawn to stateManager is supported, the unpackage
        function is currently unimplemented.
        """
        def unpackage(data):
            """Function that takes a packaged proto and unpackages item

            Currently simply returns the original data. Needs to be implemented
            """
            return data 

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
