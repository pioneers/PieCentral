import queue
import time
from LCM import *
from Utils import *

def sender():
    while True:
        command = input("Command (setup, start next, restart, score adjust, rfid): ")
        if command is None:
            continue
        if command == "setup":
            send_dict = {}
            send_dict["b1name"] = input("Blue 1 Name: ")
            send_dict["b1num"] = input("Blue 1 Num: ")
            send_dict["b2name"] = input("Blue 2 Name: ")
            send_dict["b2num"] = input("Blue 2 Num: ")

            send_dict["g1name"] = input("Gold 1 Name: ")
            send_dict["g1num"] = input("Gold 1 Num: ")
            send_dict["g2name"] = input("Gold 2 Name: ")
            send_dict["g2num"] = input("Gold 2 Num: ")

            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.SETUP_MATCH, send_dict)
        elif command == "start next":
            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.START_NEXT_STAGE)
        elif command == "restart":
            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.RESET_MATCH)
        elif command == "score adjust":
            send_dict = {}
            send_dict["blue_score"] = input("Blue Score Adjust: ")
            send_dict["gold_score"] = input("Gold jScore Adjust: ")
            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.SCORE_ADJUST, send_dict)
        elif command == "rfid":
            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.GENERATE_RFID)

def receiver():
    events = queue.Queue()
    lcm_start_read(LCM_TARGETS.UI, events)
    while True:
        event = events.get()
        print("RECEIVED:", event)

if __name__ == '__main__':
    sender_thread = threading.Thread(target=sender, name="DummyUISender")
    receiver_thread = threading.Thread(target=receiver, name="DummyUIReceiver")
    sender_thread.start()
    receiver_thread.start()
    while True:
        time.sleep(10)
