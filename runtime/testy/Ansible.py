import socket
import threading
import time
import fake_dawn
import random
import sys
from runtimeUtil import *
data = [0] #for testing purposes
sendPort = 1235
recvPort = 1236

#Custom buffer for handling states. Holds two states, updates one and sends the other.
class TwoBuffer(): 
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

sendBuffer = TwoBuffer()
recvBuffer = TwoBuffer()
raw_fake_data = [[0]]
packed_fake_data = [[0]]
dawn_buffer = [0]

###Protobuf handlers###
#Function for handling unpackaging of protobufs from Dawn
def unpackage(data):
    return data #will be changed when we fully support protos

#Handles packaging and sending state to dawn in the form of protobuf we define
def package(state, badThingsQueue):
    s = "TEST" #will be changed when we fully support protos
    b = bytearray()
    b.extend(map(ord, s))
    return b 

###Start Ansible Thread Chain###
def packageData(badThingsQueue, stateQueue, pipe):
    while True:
        try:
            rawState = pipe.recv() #Pull state from the pipe
            if rawState == SM_COMMANDS.READY:
                stateQueue.put([SM_COMMANDS.SEND, 1])
            elif rawState:
                packState = package(rawState, badThingsQueue)
                sendBuffer.replace(pack_state) ##Used list mutation as it's an atomic operation
        except Exception:
            badThingsQueue.put(BadThing(sys.exc_info(), None))

def udpSender(badThingsQueue, stateQueue, pipe):
    host = socket.gethostname()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:#DGRAM for UDP sockets
        while True: #constantly send the state to Dawn
            try:
                msg = sendBuffer.get()
                if msg != 0: #check if the data inside the buffer has changed
                    s.sendto(msg, (host, sendPort))
            except Exception:
                badThingsQueue.put(BadThing(sys.exc_info(), None))

def udpReceiver(badThingsQueue, stateQueue, pipe):
    #same thing as the client side from python docs
    host = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #DGRAM for UDP sockets
    s.bind((host, recvPort))
    while True:
        try:
            data = s.recv(2048)
            recvBuffer.replace(data)
        except Exception: 
            badThingsQueue.put(BadThing(sys.exc_info(), None))

def unpackageData(badThingsQueue, stateQueue, pipe):
    ready = False;
    while True:
        try:
            ready = pipe.recv()
            if ready:
                unpackagedData = unpackage(recvBuffer.get())
                stateQueue.put([SM_COMMANDS.STORE, unpackagedData])
        except Exception:
            badThingsQueue.put(BadThing(sys.exc_info(), None))
