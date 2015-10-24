from hibike import *
import time
import pdb

h = Hibike()
dev = [(uid, 0) for uid in h.getEnumeratedDevices()]
print(dev)
time.sleep(0.5)
pdb.set_trace()

errors = h.subToDevices(dev)
for e in errors:
	print(e)


