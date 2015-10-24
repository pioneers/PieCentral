from hibike import *

h = Hibike()
dev = h.getEnumeratedDevices()
print(dev)
errors = h.subToDevices(dev)
for e in errors:
	print(e)


