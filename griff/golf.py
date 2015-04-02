import zmq
import zmq.eventloop.zmqstream
import sys
import time

PORT = '12355'

context = zmq.Context()

socket = context.socket(zmq.PAIR)
socket.bind("tcp://127.0.0.1:%s" % PORT)
stream = zmq.eventloop.zmqstream.ZMQStream(socket)

def receive_function():
    msg = socket.recv_json()
    print msg

stream.on_recv(receive_function)

x = 0
while True:
    socket.send_json({'msg': 'server message ' + str(x)})
    x += 1
    msg = socket.recv_json()
    print msg
    print 'Sending message...'
    time.sleep(1)