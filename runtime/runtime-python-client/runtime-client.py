import zmq
import random
import sys
import time

##constructor takes in host name and port
class RuntimeClient:

    def __init__(self, address: str[]):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        self.msgid = 0
        self.socket.connect(address)
        console.log('we in bois')
        socket.send('message', )



    def set_alliance(alliance: str[]):
        msg = self.socket.recv()


class ReplyMessage :
    def __init__(self, msg):
        self.msg = msgpack.deserialize(msg)
    def toString():
        return self.msg.toString()
    def type():
        return self.msg[0]
    def msgid():
        return self.msg[1]
    def error():
        return self.msg[2]
    def result():
        return self.msg[3]
