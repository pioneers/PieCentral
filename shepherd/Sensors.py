import sys
import time
import threading
from multiprocessing import Queue
import serial # pylint: disable=import-error
from LCM import *
from Utils import *


# run "ls /dev/tty*" to obtain the two ACM ports.

buttons_gold_port = "/dev/ttyACM1" #change to correct port
buttons_blue_port = "/dev/ttyACM5" # change to correct port

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
    # maybe_ports = set(glob.glob("/dev/tty.usb*"))
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
            object_alliance = msg[0:1]
            msg_q.put((object_alliance, serial_port))
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


def recv_from_btn(ser, alliance_enum):
    print("<1> Starting Button Receive Thread", flush=True)
    while True:
        sensor_msg = ser.readline().decode("utf-8")
        sensor_msg.lower()
        payload_list = sensor_msg.split(",")
        if len(payload_list) == 1:
            continue
        payload_list[1] = payload_list[1][:-2]
        print("<2> Message Received: ", payload_list, flush=True)
        button_num = payload_list[1]
        send_dictionary = {"alliance" : alliance_enum, "button" : button_num}
        lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.LAUNCH_BUTTON_TRIGGERED, send_dictionary)
    print("sent dictionary:" + str(send_dictionary), flush=True)
    time.sleep(0.01)


def main():
    # working_ports = get_working_serial_ports(set())
    # print("working ports: ", working_ports)
    # relevant_ports = identify_relevant_ports(working_ports)
    # print("relevant ports: ", relevant_ports)

    # button_serial_blue = None
    # button_serial_gold = None

    button_serial_gold = serial.Serial(buttons_gold_port, baudrate=115200)
    button_serial_blue = serial.Serial(buttons_blue_port, baudrate=115200)

    # for alliance, port in relevant_ports:
    #     if alliance == 'b':
    #         button_serial_blue = port
    #     elif alliance == 'g':
    #         button_serial_gold = port


    button_thread_blue = threading.Thread(
        target=recv_from_btn, name="button blue", args=([button_serial_blue, ALLIANCE_COLOR.BLUE])
        )
    button_thread_gold = threading.Thread(
        target=recv_from_btn, name="buttons gold", args=([button_serial_gold, ALLIANCE_COLOR.GOLD])
        )

    button_thread_blue.daemon = True
    button_thread_gold.daemon = True

    button_thread_blue.start()
    button_thread_gold.start()

    while True:
        time.sleep(100)

if __name__ == "__main__":
    main()
