import hibike
import time
h = hibike.Hibike(timeout=1)
time.sleep(2)
x = [(uid, 100) for uid in h.getUIDs()]
print x
h.subToDevices(x)
last = ''
while 1:
	if last != str(h):
		last = str(h)
		print last
	time.sleep(.001)