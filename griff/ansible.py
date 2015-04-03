import zmq
from multiprocessing import Process, Queue
from Queue import Empty

# Sender process.
def sender(port, send_queue):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://127.0.0.1:%d" % port)
    while True:
        msg = send_queue.get()
        socket.send_json(msg)

# Receiver process.
def receiver(port, recv_queue):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://127.0.0.1:%d" % port)
    while True:
        msg = socket.recv_json()
        recv_queue.put(msg)

send_queue = None
recv_queue = None

# Initializer function. Must be called first.
def init(send_port=12355, recv_port=12356):
    global send_queue
    global recv_queue

    send_queue = Queue()
    recv_queue = Queue()

    send_process = Process(target=sender, args=(send_port, send_queue))
    recv_process = Process(target=receiver, args=(recv_port, recv_queue))
    send_process.start()
    recv_process.start()

# Sends a message. Not blocking.
def send(msg):
    send_queue.put_nowait(msg)

# Receives a message, or None if there is no current message.
def recv():
    try:
        return recv_queue.get_nowait()
    except Empty:
        return None

