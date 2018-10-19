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

def main():
    working_ports = get_working_serial_ports(set())
    print("working ports: ", working_ports)
    relevant_ports = identify_relevant_ports(working_ports)
    print("relevant ports: ", relevant_ports)


    while True:
        time.sleep(100)

if __name__ == "__main__":
    main()
