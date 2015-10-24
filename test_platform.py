from hibike import *

h = Hibike()
dev = [(uid, 0) for uid in h.getEnumeratedDevices()]
print(dev)
errors = h.subToDevices(dev)
for e in errors:
	print(e)


