import zmq
import random
import sys
import time

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)

while True:
    socket.send("Server sends an ACE")
    socket.send("Your world is mine!!!")
    msg = socket.recv()
    print msg
    time.sleep(1)