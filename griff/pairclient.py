import zmq
import random
import sys
import time

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

while True:
    msg = socket.recv()
    print msg
    socket.send("KHAAAAANNN")
    socket.send("PIEEEEEEE")
    time.sleep(0.1)