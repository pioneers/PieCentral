from Alliance import *
from Goal import *
from LCM import *
from Timer import *
from Utils import *


#initialize
class Shepherd:
    def __init__(self):
        self.queue = Queue()
        read pool of rfid tags
        lcm = LCMClass(q, LCM_TARGETS.LCM_TARGET_SHEPHERD)
        lcm.lcm_start_read()
        item = self.queue.get()
        while not item is None and item[0] is SHEPHERD_HEADER.SETUP_MATCH:
            item = self.queue.get()
        lst = item[1]
        self.Blue_Alliance = Alliance(AllIANCE_COLOR.BLUE, lst[0], lst[2],
                             lst[1], lst[3])
        self.Gold_Alliance = Alliance(AllIANCE_COLOR.GOLD, lst[4], lst[6],
                             lst[5], lst[7])
        lcm_send(LCM_TARGETS.LCM_TARGET_SCOREBOARD,SCOREBOARD_HEADER.TEAMS,*lst)


    def loop(self):
        while true:
