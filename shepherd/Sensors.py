import sys
import time
import threading
import serial
from LCM import *
from Utils import *

port_one = "/dev/ttyACM0" # change to correct port
port_two = "/dev/ttyACM1" # change to correct port

alliance_mapping = {
    "gold": ALLIANCE_COLOR.GOLD,
    "blue": ALLIANCE_COLOR.BLUE
}

goal_mapping = {
    "a": GOAL.A,
    "b": GOAL.B,
    "c": GOAL.C,
    "d": GOAL.D,
    "e": GOAL.E,
    "bg": GOAL.BLUE,
    "gg": GOAL.GOLD
}

def transfer_linebreak_data(ser):
    print("<1> Starting Linebreak Process", flush=True)
    while True:
        sensor_msg = ser.readline().decode("utf-8")
        if len(sensor_msg) != 7: #For Heartbeat
            continue
        print("<2> Message Received: ", sensor_msg)
        alliance = sensor_msg[0:4].lower()
        alliance_enum = alliance_mapping[alliance]
        goal_letter = sensor_msg[4].lower()
        if goal_letter == "g":
            alliance_letter = alliance[0] # 'b' or 'g'
            goal_enum = goal_mapping[alliance_letter + "g"]
        else:
            goal_enum = goal_mapping[goal_letter]
        send_dictionary = {"alliance" : alliance_enum, "goal" : goal_enum}
        lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.GOAL_SCORE, send_dictionary)
        time.sleep(0.01)

def main():
    goal_serial_one = serial.Serial(port_one)
    goal_serial_two = serial.Serial(port_two)

    goal_thread_one = threading.Thread(
        target=transfer_linebreak_data, name="transfer thread one", args=([goal_serial_one]))
    goal_thread_two = threading.Thread(
        target=transfer_linebreak_data, name="transfer thread two", args=([goal_serial_two]))
    goal_thread_one.daemon = True
    goal_thread_two.daemon = True

    goal_thread_one.start()
    goal_thread_two.start()

    while True:
        time.sleep(100)

if __name__ == "__main__":
    main()
