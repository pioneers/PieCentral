import hibike
import time
h = hibike.Hibike(timeout=1)
last = ''
while 1:
	if last != str(h):
		last = str(h)
		print last
	time.sleep(.001)