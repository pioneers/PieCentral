import queue
from LCM import *
from Utils import *

if __name__ == '__main__':
    events = queue.Queue()
    lcm_start_read(str.encode(LCM_TARGETS.SHEPHERD), events)
    while True:
        event = events.get()
        print("RECEIVED:", event)
