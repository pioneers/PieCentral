'''
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
            bName1 = input("Blue 1 Name: ")
            bNum1 = input("Blue 1 Num: ")
            bName2 = input("Blue 2 Name: ")
            bNum2 = input("Blue 2 Num: ")

            gName1 = input("Gold 1 Name: ")
            gNum1 = input("Gold 1 Num: ")
            gName2 = input("Gold 2 Name: ")
            gNum2 = input("Gold 2 Num: ")

            #lcm_send(#lcm_TARGETS.SHEPHERD, SHEPHERD_HEADER.SETUP_MATCH,
                     #bName1, bNum1, bName2, bNum2, gName1, gNum1, gName2, gNum2)

        elif command == "start next":
            #lcm_send(#lcm_TARGETS.SHEPHERD, SHEPHERD_HEADER.START_NEXT_STAGE)
            pass
        elif command == "restart match":
            #lcm_send(#lcm_TARGETS.SHEPHERD, SHEPHERD_HEADER.RESET_MATCH)
            pass
        elif command == "score adjust":
            blueAdjust = input("Blue Score Adjust: ")
            goldAdjust = input("Gold Score Adjust: ")
            #lcm_send(#lcm_TARGETS.SHEPHERD, SHEPHERD_HEADER.SCORE_ADJUST, blueAdjust, goldAdjust)

        elif command == "rfid":
            #lcm_send(#lcm_TARGETS.SHEPHERD, SHEPHERD_HEADER.GENERATE_RFID)



def receiver():
    events = queue.Queue()
    #lcm_start_read(str.encode(#lcm_TARGETS.UI), events)
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
'''
