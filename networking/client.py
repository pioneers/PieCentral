import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--persistent", help="persistent sending mode",
                    action="store_true")
parser.add_argument("--ip", default='localhost',
                    help="destination ip, default localhost")
parser.add_argument("--port", default='3141',
                    help="connection port, default 3141")
args = parser.parse_args()


HOST = args.ip
PORT = int(args.port)
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        msg = bytes(input('message: '), 'UTF8')
        s.sendall(msg)
    if not args.persistent:
        break

