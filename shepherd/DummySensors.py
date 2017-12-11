import threading
import queue
from LCM import *
from Utils import *

def sender():
    input_to_header = {
        "score" : SHEPHERD_HEADER.GOAL_SCORE,
        "bid"   : SHEPHERD_HEADER.GOAL_BID,
        "code"  : SHEPHERD_HEADER.CODE_INPUT,
    }

    input_to_alliance = {
        "gold"  : ALLIANCE_COLOR.GOLD,
        "blue"  : ALLIANCE_COLOR.BLUE,
    }

    input_to_goal = {
        "a"     : GOAL.A,
        "b"     : GOAL.B,
        "c"     : GOAL.C,
        "d"     : GOAL.D,
        "e"     : GOAL.E,
        "gold"  : GOAL.GOLD,
        "blue"  : GOAL.BLUE,
    }

    while True:
        new_input = input_to_header.get(input("Command: score bid code "))
        if new_input == SHEPHERD_HEADER.GOAL_SCORE or new_input == SHEPHERD_HEADER.GOAL_BID:
            goal_letter = input_to_goal.get(input("Goal Letter: a b c d e blue gold "))
            alliance = input_to_alliance.get(input("Alliance: blue gold "))
            if goal_letter is None or alliance is None:
                print("Invalid input")
                continue
            lcm_send(LCM_TARGETS.SHEPHERD, new_input, goal_letter, alliance)
        else:
            print("Invalid input")

def receiver():
    events = queue.Queue()
    lcm_start_read(LCM_TARGETS.SENSORS, events)
    while True:
        event = events.get(True)
        print(event)

if __name__ == "__main__":
    sender_thread = threading.Thread(target=sender, name="DummySensorSender")
    recv_thread = threading.Thread(target=receiver, name="DummySensorReceiver")
    sender_thread.start()
    recv_thread.start()
