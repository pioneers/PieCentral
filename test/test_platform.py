from hibike import Hibike
import hibike_message as hm
import time
import pdb
import binascii

h = Hibike()
hm.send(h.serialToUID.values()[0][1], hm.make_sub_request(0))

# devices = h.getUIDs()
# pdb.set_trace()

# while 1:
# 	val = input("enter servo value: ")
# 	if val == -1:
# 		break
# 	c.writeValue(device.uid, "servo0", int(val))
# 	time.sleep(0.2)
# 	print(c.getData(device.uid, "servo0"))
