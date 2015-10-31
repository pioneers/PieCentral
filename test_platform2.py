from hibike import Hibike
from hibike_message import *
h = Hibike()
devices = h.getEnumeratedDevices()
uid = devices.keys()[0]
# h.subToDevices([(uid, 250)])
