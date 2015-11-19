from hibike import Hibike
from deviceContext import DeviceContext
import hibike_message as hm
import time
import binascii

c = DeviceContext()
h = Hibike(c)
devices = c.devices.values()
device = devices[0]
# for device in devices:
#     print device
#     c.subToDevice(device.uid, 10)
# time.sleep(1)
# while 1:
#     for device in devices:
#         print binascii.hexlify(device.getParam("dataUpdate"))
        #time.sleep(.1)

while 1:
	val = input("enter servo value: ")
	if val == -1:
		break
	c.writeValue(device.uid, "servo0", int(val))
	time.sleep(0.2)
	print(c.getData(device.uid, "servo0"))
