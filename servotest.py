import hibike
import time

h = hibike.Hibike()
d = h.getEnumeratedDevices()[0][0]

def setservos(n):
    h.writeValue(d, 'servo0', n)
    h.writeValue(d, 'servo1', n)
    h.writeValue(d, 'servo2', n)
    h.writeValue(d, 'servo3', n)

def readservos():
    print h.getData(d, 'servo0')
    print h.getData(d, 'servo1')
    print h.getData(d, 'servo2')
    print h.getData(d, 'servo3')


