from flask import Flask, copy_current_request_context, request
from flask.ext.socketio import SocketIO
from multiprocessing import Process, Queue
from Queue import Empty

def socket_server(recv_queue, send_queue):
    app = Flask(__name__)
    socketio = SocketIO(app)

    @socketio.on('message')
    def receive_message(msg):
        print msg
        recv_queue.put_nowait(msg)

    @socketio.on('connect')
    def on_connect():
        socketio.emit('message', 'test')
        print 'Connected to Dawn.'

    @socketio.on_error()
    def on_error(e):
        print e

    def send_process(send_queue):
        while True:
            msg = send_queue.get()
            socketio.emit('message', msg)

    send_p = Process(target=send_process, args=(send_queue,))
    send_p.start()

    socketio.run(app)

# DON'T USE THIS UNLESS YOU KNOW WHAT YOU'RE DOING
# Low level message sending. For high level messaging, use send_msg.
def send(msg):
    send_queue.put_nowait(msg)

# Use this one instead of send
def send_message(msg_type, content):
    send({
        'header': {'msg_type': msg_type},
        'content': content
    })

# Receives a message, or None if there is no current message.
# If block is True, blocks.
def recv(block=False):
    if block:
        return recv_queue.get()
    else:
        try:
            return recv_queue.get_nowait()
        except Empty:
            return None

recv_queue = Queue()
send_queue = Queue()

socket_p = Process(target=socket_server, args=(recv_queue, send_queue))
socket_p.start()
