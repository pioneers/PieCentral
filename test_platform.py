import hibike
from hibike_message import *
import time
import serial
import pdb
import os
# h = Hibike()
# dev = [(uid, 0) for uid in h.getEnumeratedDevices()]
# print(dev)
# time.sleep(0.5)
# pdb.set_trace()

# errors = h.subToDevices(dev)
# for e in errors:
# 	print(e)
ports = ['/dev/%s' % port for port in os.listdir("/dev/") 
                if port[:6] == "ttyUSB"]
s = serial.Serial(ports[0], 115200)

pay = struct.pack("<H", 100)

msg = HibikeMessage(0, pay)

time.sleep(0.5)

def do():
	print(s.inWaiting())
	send(msg, s)
	time.sleep(0.01)
	print(s.inWaiting())

def show():
    print(read(s))
	cache = 0
	while(1):
		while(s.inWaiting()):
			cache = struct.unpack("<B",read(s).getPayload())[0]
		print cache
