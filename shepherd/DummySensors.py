import threading
import queue
from LCM import *
from Utils import *

def sender():
    input_to_header = {
        "score" : SHEPHERD_HEADER.GOAL_SCORE,
        "bid"   : SHEPHERD_HEADER.GOAL_BID,
        "code"  : SHEPHERD_HEADER.POWERUP_APPLICATION,
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
        if new_input in (SHEPHERD_HEADER.GOAL_SCORE, SHEPHERD_HEADER.GOAL_BID):
            goal_letter = input_to_goal.get(input("Goal Letter: a b c d e blue gold "))
            alliance = input_to_alliance.get(input("Alliance: blue gold "))
            if goal_letter is None or alliance is None:
                print("Invalid input")
                continue
            if new_input == SHEPHERD_HEADER.GOAL_SCORE:
                for _ in range(0):
                    lcm_send(LCM_TARGETS.SHEPHERD, new_input, {"alliance" : alliance,
                                                               "goal" : goal_letter})
            lcm_send(LCM_TARGETS.SHEPHERD, new_input, {"alliance" : alliance, "goal" : goal_letter})

        elif new_input == SHEPHERD_HEADER.POWERUP_APPLICATION:
            goal_letter = input_to_goal.get(input("Goal Letter: a b c d e blue gold "))
            alliance = input_to_alliance.get(input("Alliance: blue gold "))
            code = input("Code: ")
            if goal_letter is None or alliance is None or code is None:
                print("Invalid input")
                continue
            lcm_send(LCM_TARGETS.SHEPHERD, new_input, {"alliance" : alliance,
                                                       "goal" : goal_letter,
                                                       "code" : code})
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
