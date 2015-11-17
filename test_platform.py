from hibike import Hibike
from deviceContext import DeviceContext
import time
import binascii
from sys import stdout
c = DeviceContext()
h = Hibike(c)
devices = c.devices.values()
for device in devices:
    print device
time.sleep(1)
len_curr = 0
x = devices[0]
c.readValue(x.uid, 1)
def show():
    for device in devices:
        print device
def display():
    while 1:
        show()
        time.sleep(.01)
# while 1:
#     out = ""
#     for device in devices:
#         out += binascii.hexlify(device.getParam("dataUpdate"))
#     print out
#     time.sleep(.001)