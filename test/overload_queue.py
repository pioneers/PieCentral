import hibike
import time
h = hibike.Hibike(timeout=1)
time.sleep(2)
pot   = [uid for uid in h.getUIDs() if h.getDeviceName(h.getDeviceType(uid)) == 'Potentiometer'][0]
servo = [uid for uid in h.getUIDs() if h.getDeviceName(h.getDeviceType(uid)) == 'ServoControl'][0]
h.subToDevice(pot, 10)
last = ''
while 1:
    if 1:
        last = h.getData(pot, 0)
        for i in range(1,5):
            h.writeValue(servo, i, int(h.getData(pot, 0)[i - 1] * 180))
        print h.sendBuffer.qsize()
        print str(h)

    time.sleep(.001)