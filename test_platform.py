import hibike
from hibike_message import *
import time
import serial
import pdb

# h = Hibike()
# dev = [(uid, 0) for uid in h.getEnumeratedDevices()]
# print(dev)
# time.sleep(0.5)
# pdb.set_trace()

# errors = h.subToDevices(dev)
# for e in errors:
# 	print(e)

s = serial.Serial('/dev/ttyUSB5', 115200)

pay = bytearray()
pay.append(0)
msg = HibikeMessage(1, pay)

time.sleep(0.5)

def do():
	print(s.inWaiting())
	send(msg, s)
	time.sleep(0.01)
	print(s.inWaiting())
