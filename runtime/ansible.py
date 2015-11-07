import zmq, yaml
from multiprocessing import Process, Queue
from Queue import Empty

class AMessage(object):
    """Convenience class for sending Ansible Messages
    DEPRECATED DON'T USE THIS
    """

    def __init__(self, msg_type, content):
        assert isinstance(msg_type, basestring)
        self.msg_type = msg_type
        self.content = content

    @property
    def as_dict(self):
        return {
            'header': {'msg_type': self.msg_type},
            'content': self.content
        }

# Sender process.
def sender(port, send_queue, do_bind=True):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    if do_bind:
       f=socket.bind
    else:
       f = socket.connect
    f("tcp://127.0.0.1:%d" % port)
    while True:
        msg = send_queue.get()
        if isinstance(msg, AMessage):
            msg = msg.as_dict
        socket.send_json(msg)

# Receiver process.
def receiver(port, recv_queue, do_bind=True):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    if do_bind:
        f = socket.bind
    else:
        f=socket.connect
    f("tcp://127.0.0.1:%d" % port)
    while True:
        msg = socket.recv()
        parsed = yaml.load(msg)
        recv_queue.put(parsed)


class Ansible(object):
# Doesn't do anything.
    def __init__(self, role):
        # Intialize on module import
        if (role == 'dawn'):
            self.send_port = 12355
            self.recv_port = 12356
        elif (role == 'runtime'):
            self.send_port = 12357
            self.recv_port = 12358
        elif (role == 'student_code'):
            print('student code')
            self.send_port = 12358
            self.recv_port = 12357
        else:
            raise ValueError()

        self.send_queue = Queue()
        self.recv_queue = Queue()

        self.send_process = Process(target=sender, args=(self.send_port, self.send_queue,
                                                         role != 'student_code'))
        self.recv_process = Process(target=receiver, args=(self.recv_port, self.recv_queue,
                                                           role != 'student_code'))
        self.send_process.start()
        self.recv_process.start()


    # DON'T USE THIS UNLESS YOU KNOW WHAT YOU'RE DOING
    # Low level message sending. For high level messaging, use send_msg.
    def send(self, msg):
        self.send_queue.put_nowait(msg)

    # Use this one instead of send
    def send_message(self, msg_type, content):
        self.send({
            'header': {'msg_type': msg_type},
            'content': content
        })

    # Receives a message, or None if there is no current message.
    # If block is True, blocks.
    def recv(self, block=False):
        if block:
            return self.recv_queue.get()
        else:
            try:
                return self.recv_queue.get_nowait()
            except Empty:
                return None

