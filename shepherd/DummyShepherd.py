import queue
import time
from LCM import *
from Utils import *

if __name__ == '__main__':
    while True:
        msg = {"autonomous": True, "enabled": True}
        lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.ROBOT_STATE, msg)

        time.sleep(1)
        msg2 = {"autonomous": False, "enabled": False}
        lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.ROBOT_STATE, msg2)
        time.sleep(1)

        lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.CODES, {"rfids" : [1, 2, 3, 4, 5, 6],
                                                       "codes" : [1, 2, 3, 4, 5, 6],
                                                       "solutions" : [1, 2, 3, 4, 5, 6]})
