import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default='localhost',
                    help="client ip, default localhost")
parser.add_argument("--port", default='3141',
                    help="connection port, default 3141")

args = parser.parse_args()

HOST = args.ip
PORT = int(args.port)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        msg = bytes()
        data = conn.recv(1024)
        while data:
            msg += data
            data = conn.recv(1024)
        print(msg.decode('UTF8'))
