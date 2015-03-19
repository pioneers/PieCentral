import zmq 
import random 
import sys 
import time 

PORT = "5556" 

context = zmq.Context() 

socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" %PORT)

while True:
	socket.send("Server message to client")
	msg = socket.recv() 
	print msg 
	time.sleep(1)