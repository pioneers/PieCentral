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
            send_dict["b1name"] = "Hayward"
            send_dict["b1num"] = 31
            send_dict["b2name"] = "El Cerrito"
            send_dict["b2num"] = 4

            send_dict["g1name"] = "Middle College"
            send_dict["g1num"] = 36
            send_dict["g2name"] = "Brandon"
            send_dict["g2num"] = 8

            send_dict["match_num"] = 9

            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.SETUP_MATCH, send_dict)
        elif command == "start next":
            print("TESTING")
            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.START_NEXT_STAGE)
        elif command == "restart":
            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.RESET_MATCH)
        elif command == "score adjust":
            send_dict = {}
            send_dict["blue_score"] = input("Blue Score Adjust: ")
            send_dict["gold_score"] = input("Gold Score Adjust: ")
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
