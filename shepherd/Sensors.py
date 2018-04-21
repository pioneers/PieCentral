import sys
import time
import threading
from multiprocessing import Queue
import serial
from LCM import *
from Utils import *

linebreak_port_one = "/dev/ttyACM0" # change to correct port
linebreak_port_two = "/dev/ttyACM0" # change to correct port
bidding_port_blue = "/dev/ttyACM0" # change to correct port
bidding_port_gold = "/dev/ttyACM0" # change to correct port

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

IDENTIFY_TIMEOUT = 5

def get_working_serial_ports(excludes: set):
    """Get a list of working serial ports, excluding some.
    Returns a list of `serial.Serial` object.
    """
    import glob
    maybe_ports = set(glob.glob("/dev/ttyACM*"))
    maybe_ports.difference_update(excludes)

    working = []
    for p in maybe_ports:
        try:
            working.append(serial.Serial(p, baudrate=115200))
        except serial.SerialException:
            pass

    return working


def identify_relevant_ports(working_ports):
    """ Check which ports have linebreak sensors or bidding stations on them.
    Returns a list of tuples containing the object type, alliance,
    and its corresponding serial port.
    """
    def maybe_identify_sensor(serial_port, timeout, msg_q):
        """Check whether a serial port contains a sensor.
        Parameters:
            serial_port -- the port to check
            timeout -- quit reading from the serial port after this
            amount of time
            msg_q -- a queue to set if a device is successfully identified
        """
        prev_timeout = serial_port.timeout
        serial_port.timeout = timeout
        try:
            msg = serial_port.readline().decode("utf-8")
            if is_linebreak_sensor(msg) or is_bidding_station(msg):
                object_type = msg[0:2]
                object_alliance = msg[2:3]
                msg_q.put((object_type, object_alliance, serial_port))
        except serial.SerialTimeoutException:
            pass
        serial_port.timeout = prev_timeout

    msg_q = Queue()
    threads = [threading.Thread(target=maybe_identify_sensor,
                                args=(port,
                                      IDENTIFY_TIMEOUT,
                                      msg_q)) for port in working_ports]
    for thread in threads:
        thread.start()

    time.sleep(IDENTIFY_TIMEOUT)
    for thread in threads:
        thread.join()
    # parse through queue and make appropriate tuples
    sensor_ports = []
    while not msg_q.empty():
        sensor_ports += [msg_q.get()]
    return sensor_ports


def is_linebreak_sensor(sensor_msg):
    """Check whether a message is sent from a linebreak sensor."""
    return sensor_msg[0:2] == "lb"

def is_bidding_station(sensor_msg):
    """Check whether a message is sent from a linebreak sensor."""
    return sensor_msg[0:2] == "bs"


def recv_from_bid(ser, alliance_enum):
    print("<3> Starting Bid Station Receive Thread", flush=True)
    while True:
        sensor_msg = ser.readline().decode("utf-8")
        sensor_msg.lower()
        payload_list = sensor_msg.split(";")
        if len(payload_list) == 2 and payload_list[1] == "hb\r\n":
            continue
        print("<4> Message Received: ", payload_list, flush=True)
        payload_list = payload_list[1:]
        if payload_list[0] == "bg":
            goal_enum = goal_mapping[payload_list[1][0]]
            send_dictionary = {"goal": goal_enum, "alliance": alliance_enum}
            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.GOAL_BID, send_dictionary)
        elif payload_list[0] == "csub":
            goal_enum = goal_mapping[payload_list[2][0]]
            code = int(payload_list[1])
            send_dictionary = {"alliance": alliance_enum, "goal": goal_enum, "code": code}
            lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.POWERUP_APPLICATION, send_dictionary)
        else:
            time.sleep(.01)
            continue
        print("sent dictionary:" + str(send_dictionary), flush=True)
        time.sleep(0.01)

def send_to_bid(ser, alliance_enum):
    print("<4> Starting Bid Station Send Thread", flush=True)
    recv_q = Queue()
    lcm_start_read(LCM_TARGETS.SENSORS, recv_q)
    while True:
        msg = recv_q.get()
        payload_dict = msg[1]
        send_str = ""
        if msg[0] == SENSOR_HEADER.BID_PRICE:
            send_str = "bp;"
            goal_list = payload_dict["price"]
            if alliance_enum == ALLIANCE_COLOR.BLUE:
                goal_list = goal_list[::-1]
            for price in goal_list:
                send_str += str(price) + ";"
            send_str += '\r\n'
        elif msg[0] == SENSOR_HEADER.TEAM_SCORE:
            send_str = "ts;"
            score = str(payload_dict["score"][alliance_enum])
            send_str += score + ";\r\n"
        elif msg[0] == SENSOR_HEADER.CODE_RESULT:
            if alliance_enum != payload_dict["alliance"]:
                continue
            send_str = "cstatus;"
            send_str += str(payload_dict["result"]) + ";\r\n"
        elif msg[0] == SENSOR_HEADER.GOAL_OWNERS:
            send_str = "go;"
            owners_list = payload_dict["owners"]
            bidders_list = payload_dict["bidders"]
            for i in range(len(owners_list)):
                owner = owners_list[i]
                owner_color = ""
                if owner is None:
                    owner_color = "n"
                elif owner == ALLIANCE_COLOR.BLUE:
                    owner_color = "b"
                else:
                    owner_color = "g"
                bidder = bidders_list[i]
                if bidder is None:
                    send_str += owner_color
                elif bidder == alliance_enum and alliance_enum == ALLIANCE_COLOR.BLUE:
                    send_str += "L" #Set LED to red, so we can't bid on it again
                elif bidder == alliance_enum and bidder == ALLIANCE_COLOR.GOLD:
                    send_str += "L" #Set LED to red, so we can't bid on it
                else:
                    send_str += "e"
                send_str += ";"
            send_str += "\r\n"
        print(send_str, flush=True)
        print(send_str.encode("utf-8"))
        ser.write(send_str.encode("utf-8"))
        time.sleep(.05)

def transfer_linebreak_data(ser):
    print("<1> Starting Linebreak Process", flush=True)
    count = 0
    while True:
        sensor_msg = ser.readline().decode("utf-8")
        if len(sensor_msg) != 11: #For Heartbeat
            continue
        print("<2> Message Received: ", sensor_msg, count, flush=True)
        count += 1
        sensor_msg = sensor_msg[4:] #Remove identification tag
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
    working_ports = get_working_serial_ports(set())
    print("working ports: ", working_ports)
    relevant_ports = identify_relevant_ports(working_ports)
    print("relevant ports: ", relevant_ports)

    goal_serial_one = None
    goal_serial_two = None
    bid_serial_blue = None
    bid_serial_gold = None

    for obj_type, alliance, port in relevant_ports:
        if obj_type == 'lb' and alliance == 'b':
            goal_serial_one = port
        elif obj_type == 'lb' and alliance == 'g':
            goal_serial_two = port
        elif obj_type == 'bs' and alliance == 'b':
            bid_serial_blue = port
        elif obj_type == 'bs' and alliance == 'g':
            bid_serial_gold = port

    goal_thread_one = threading.Thread(
        target=transfer_linebreak_data, name="transfer thread one", args=([goal_serial_one]))
    goal_thread_two = threading.Thread(
        target=transfer_linebreak_data, name="transfer thread two", args=([goal_serial_two]))
    goal_thread_one.daemon = True
    goal_thread_two.daemon = True

    goal_thread_one.start()
    goal_thread_two.start()

    recv_thread_blue = threading.Thread(
        target=recv_from_bid, name="receive thread blue",
        args=([bid_serial_blue, ALLIANCE_COLOR.BLUE]))
    send_thread_blue = threading.Thread(
        target=send_to_bid, name="send thread blue",
        args=([bid_serial_blue, ALLIANCE_COLOR.BLUE]))

    recv_thread_gold = threading.Thread(
        target=recv_from_bid, name="receive thread gold",
        args=([bid_serial_gold, ALLIANCE_COLOR.GOLD]))
    send_thread_gold = threading.Thread(
        target=send_to_bid, name="send thread gold",
        args=([bid_serial_gold, ALLIANCE_COLOR.GOLD]))

    recv_thread_blue.daemon = True
    send_thread_blue.daemon = True
    recv_thread_gold.daemon = True
    send_thread_gold.daemon = True

    recv_thread_blue.start()
    send_thread_blue.start()
    recv_thread_gold.start()
    send_thread_gold.start()

    while True:
        time.sleep(100)

if __name__ == "__main__":
    main()
