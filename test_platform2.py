from hibike import Hibike
from hibike_message import *
import time
import pdb

hib = Hibike()
devices = hib.getEnumeratedDevices()
uid = devices.keys()[0]
hib.subToDevices([(uid, 10)])

while 1:
	time.sleep(0.01)
	# pdb.set_trace()
	print(struct.unpack("<B", hib.getData(uid))[0])

