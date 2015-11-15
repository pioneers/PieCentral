from hibike import Hibike
from deviceContext import DeviceContext
import time
import binascii
c = DeviceContext()
h = Hibike(c)
devices = c.devices.values()
for device in devices:
    print device
    c.subToDevice(device.uid, 10)
time.sleep(1)
while 1:
    for device in devices:
        print binascii.hexlify(device.getParam("dataUpdate"))
        #time.sleep(.1)