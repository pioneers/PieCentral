import LCM
import queue
from Utils import *

if __name__ == "__main__":
    event_queue = queue.Queue()
    LCM.lcm_start_read(LCM_TARGETS.SCOREBOARD, event_queue)
    while True:
        print(event_queue.get(True))


