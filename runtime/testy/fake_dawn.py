import socket
import threading
import queue
import time

data = [0]
send_port = 1236
recv_port = 1235
dawn_hz = 10

def sender(port, send_queue):
	host = '127.0.0.1'
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		while True:
			next_call = time.time()
			msg = None
			string = "From Dawn" 
			b = bytearray()
			b.extend(map(ord, string))
			msg = bytes(b)
			s.sendto(msg, (host, send_port))
			next_call += 1.0/dawn_hz
			if next_call > time.time():
				time.sleep(next_call - time.time())

def receiver(port, receive_queue):
	host = '127.0.0.1'
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((host, recv_port))
	while True:
		msg, addr = s.recvfrom(2048)
		receive_queue[0]=msg

sender_thread = threading.Thread(target = sender, name = "fake dawn sender", args = (send_port, data))
recv_thread = threading.Thread(target = receiver, name = "fake dawn receiver", args = (recv_port, data))
sender_thread.daemon = True
recv_thread.daemon = True
recv_thread.start()
sender_thread.start()

#Just Here for testing, should not be run regularly
while True:
	print(data)
	time.sleep(1)
