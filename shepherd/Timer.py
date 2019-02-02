import time
import threading
import collections
import heapq
import LCM
from Utils import *

class busyThread(threading.Thread):
    '''
    Subclass that is the actual thread that will be running.
    There will only be one for the entire class.
    '''
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.stop = threading.Event()

    def run(self):
        '''
        When started, thread will run and process Timers in queue until manually stopped
        TODO: Add how to send message via LCM in the case of match timer
        '''
        while not self.stop.isSet():
            if self.queue and self.queue[0].end_time < time.time():
                Timer.queueLock.acquire()
                event = heapq.heappop(self.queue)
                if event.timer_type == TIMER_TYPES.MATCH:
                    LCM.lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.STAGE_TIMER_END)
                if event.timer_type == TIMER_TYPES.EXTENDED_TELEOP:
                    LCM.lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.END_EXTENDED_TELEOP)
                event.active = False
                Timer.queueLock.release()
        for timer in self.queue:
            timer.active = False

    def join(self, timeout=None):
        '''Stops this thread. Must be called from different thread (Main Thread)'''
        self.stop.set()
        super().join(timeout)
        Timer.running = False

class Timer:
    """
    This class should spawn another thread that will keep track of a target time
    and compare it to the current system time in order to see how much time is left
    """

    eventQueue = []
    thread = busyThread(eventQueue)
    running = False
    queueLock = threading.Lock()
    globalResetCount = 0
    reset_all_count = 0

    def __init__(self, timer_type):
        """
        timer_type - a Enum representing the type of timer that this is:
                        TIMER_TYPES.MATCH - represents the time of the current
        """
        self.active = False
        self.timer_type = timer_type
        self.end_time = None
        self.reset_all_count = Timer.globalResetCount

    def start_timer(self, duration):
        """Starts a new timer with the duration (seconds) and sets timer to active.
           If Timer is already running, adds duration to Timer"""
        self.reset_all_count = Timer.globalResetCount
        if self.active:
            Timer.queueLock.acquire()
            self.end_time += duration
            heapq.heapify(Timer.eventQueue)
            Timer.queueLock.release()
        else:
            if not Timer.running:
                Timer.running = True
                Timer.thread.start()
            Timer.queueLock.acquire()
            self.end_time = time.time() + duration
            heapq.heappush(Timer.eventQueue, self)
            self.active = True
            Timer.queueLock.release()


    def reset(self):
        """Stops the current timer (if any) and sets timer to inactive"""
        if self.active and self.reset_all_count == Timer.globalResetCount:
            Timer.queueLock.acquire()
            Timer.eventQueue.remove(self)
            heapq.heapify(Timer.eventQueue)
            self.active = False
            Timer.queueLock.release()

    def is_running(self):
        """Returns true if the timer is currently running"""
        return self.active

    @classmethod
    def reset_all(cls):
        """Resets Timer Thread when game changes"""
        if cls.running:
            cls.thread.join()
            cls.eventQueue = []
            cls.thread = busyThread(cls.eventQueue)
            cls.running = False
            cls.queueLock = threading.Lock()
            cls.globalResetCount = cls.globalResetCount + 1

    ###########################################
    # Timer Comparison Methods
    ###########################################
    def __lt__(self, other):
        return self.end_time < other.end_time

    def __gt__(self, other):
        return self.end_time > other.end_time

    def __eq__(self, other):
        return self.end_time == other.end_time
