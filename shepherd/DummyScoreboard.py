import queue
import LCM
from Utils import *

if __name__ == "__main__":
    events = queue.Queue()
    LCM.lcm_start_read(LCM_TARGETS.SCOREBOARD, events)
    while True:
        print(events.get(True))
