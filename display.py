import hibike
import time
h = hibike.Hibike(timeout=1)
time.sleep(2)
x = [(uid, 100) for uid in h.getUIDs()]
uid_params = {uid: h.getParams(uid)[1:] for uid in h.getUIDs()}
print x
h.subToDevices(x)
last = ''
counter = 0
while 1:
    counter += 1
    if last != str(h):
        last = str(h)
        print last
    if counter % 1000 == 0:
        for uid in uid_params:
            for param in uid_params[uid]:
                h.readValue(uid, param)
        counter = 0
    time.sleep(.001)