"""Emulate an instance of Dawn."""

import socket
import threading
import queue
import time
import runtime_pb2
import ansible_pb2
import notification_pb2

DATA = [0]
SEND_PORT = 1236
RECV_PORT = 1235
TCP_PORT = 1234
DAWN_HZ = 100


def dawn_packager():
    """Create a sample Dawn message."""
    proto_message = ansible_pb2.DawnData()
    proto_message.student_code_status = ansible_pb2.DawnData.TELEOP
    test_gamepad = proto_message.gamepads.add()
    test_gamepad.index = 0
    test_gamepad.axes.append(.5)
    test_gamepad.buttons.append(True)
    return proto_message.SerializeToString()


def sender(_port, _send_queue):
    """Send a sample dawn message on ``port``."""
    host = '127.0.0.1'
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        while True:
            next_call = time.time()
            msg = dawn_packager()
            sock.sendto(msg, (host, SEND_PORT))
            next_call += 1.0 / DAWN_HZ
            time.sleep(max(next_call - time.time(), 0))


def receiver(_port, receive_queue):
    """Receive messages on port to receive queue."""
    host = '127.0.0.1'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, RECV_PORT))
    while True:
        msg, _ = sock.recvfrom(2048)
        runtime_message = runtime_pb2.RuntimeData()
        runtime_message.ParseFromString(msg)
        receive_queue[0] = msg


def add_timestamps(msgqueue):
    """Add timestamp messages to ``msgqueue``."""
    for _ in range(10):
        msg = notification_pb2.Notification()
        msg.header = notification_pb2.Notification.TIMESTAMP_DOWN
        msg.timestamps.append(time.perf_counter())
        msg = msg.SerializeToString()
        msgqueue.put(msg)
    return msgqueue


def tcp_relay(port, msgqueue=queue.Queue()):
    """Sends and receives messages on ``port``."""
    host = '127.0.0.1'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)
    conn, _ = sock.accept()
    while True:
        if not msgqueue.empty():
            conn.send(msgqueue.get())
        next_call = time.time()
        next_call += 1.0 / DAWN_HZ
        receive_msg, _ = conn.recvfrom(2048)
        if receive_msg is None:
            continue
        else:
            parser = notification_pb2.Notification()
            parser.ParseFromString(receive_msg)
            if parser.timestamps:
                print(parser.timestamps)
        time.sleep(max(next_call - time.time(), 0))


SENDER_THREAD = threading.Thread(
    target=sender, name="fake dawn sender", args=(SEND_PORT, DATA))
RECV_THREAD = threading.Thread(
    target=receiver, name="fake dawn receiver", args=(RECV_PORT, DATA))
SENDER_THREAD.daemon = True
RECV_THREAD.daemon = True
RECV_THREAD.start()
SENDER_THREAD.start()
MSGQUEUE = queue.Queue()
TCP_THREAD = threading.Thread(
    target=tcp_relay, name="fake dawn tcp", args=([TCP_PORT, MSGQUEUE]))
TCP_THREAD.daemon = True
TCP_THREAD.start()
print("started threads")
add_timestamps(MSGQUEUE)

# Just Here for testing, should not be run regularly
if __name__ == "__main__":
    while True:
        time.sleep(1)
