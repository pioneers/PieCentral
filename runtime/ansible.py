from multiprocessing import Process, Queue
from Queue import Empty
from ansible_server import ansible_server

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
def recv():
    try:
        return recv_queue.get_nowait()
    except Empty:
        return None

# Start up the Flask-SocketIO server
send_queue = Queue()
recv_queue = Queue()
ansible_p = Process(target=ansible_server, args=(send_queue, recv_queue))
ansible_p.start()

