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
#   print(e)
ports = ['/dev/%s' % port for port in os.listdir("/dev/") 
                if port[:6] == "ttyUSB"]
s = serial.Serial(ports[0], 115200)

pay = struct.pack("<H", 0)

msg = HibikeMessage(0, pay)

msg2 = HibikeMessage(messageTypes['DeviceUpdate'], struct.pack("<BI", 8, 5))

time.sleep(2)

def do():
  print("sending ping and device update with param, value = 8, 5")
  #print(s.inWaiting())
  send(s, msg)
  send(s, msg2)
  time.sleep(0.01)
  #print(s.inWaiting())
  print "sub response (should be 0):", struct.unpack("<HBQH", read(s).getPayload())[3]
  print "device response (should be (8, 5)):", struct.unpack("<BI", read(s).getPayload())
do()

def show():
  period = 1
  send(HibikeMessage(0, struct.pack("<H", period)), s)
  time.sleep(0.1)
  read(s)
  print "showing DataUpdates with period", period
  cache = 0
  while(1):
    while(s.inWaiting()):
      cache = struct.unpack("<B",read(s).getPayload())[0]
      print cache
show()
