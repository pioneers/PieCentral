import csv
import subprocess
import shlex
import re
import os
import atexit
import time

popens = []
devices_to_spawn = ["LimitSwitch", "LimitSwitch", "ServoControl", "Potentiometer"]

def get_virtual_ports():
    socat = subprocess.Popen(shlex.split("socat -d -d pty,raw,echo=0 pty,raw,echo=0"), stderr=subprocess.PIPE)
    popens.append(socat)
    lines = [str(socat.stderr.readline()), str(socat.stderr.readline())]
    p1 = re.search(r'PTY is (/dev/pts/\d+)', lines[0]).group(1)
    p2 = re.search(r'PTY is (/dev/pts/\d+)', lines[1]).group(1)
    return p1, p2

def spawn_device(device_type):
    p1, p2 = get_virtual_ports()
    fname = os.path.join(os.path.dirname(__file__), "virtual_device.py")
    device = subprocess.Popen(shlex.split("python3 %s -d %s -p %s" % (fname, device_type, p1)))
    popens.append(device)
    return p2

@atexit.register
def cleanup():
    for process in popens:
        process.kill()


if __name__ == "__main__":
    with open("virtual_devices.txt", "w+") as device_file:
        devices = [spawn_device(device_type) for device_type in devices_to_spawn]
        device_file.write(" ".join(devices))
    while True:
        time.sleep(1)
