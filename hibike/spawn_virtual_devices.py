# Licensed to Pioneers in Engineering under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Pioneers in Engineering licenses
# this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
"""
Spawn virtual devices.
"""
import subprocess
import shlex
import re
import os
import atexit
import time

POPENS = []
DEVICES_TO_SPAWN = ["LimitSwitch", "LimitSwitch", "ServoControl", "Potentiometer", "YogiBear"]

def get_virtual_ports():
    """
    Spawn two virtual serial ports, returning them.
    """
    socat = subprocess.Popen(shlex.split("socat -d -d pty,raw,echo=0 pty,raw,echo=0"),
                             stderr=subprocess.PIPE)
    POPENS.append(socat)
    lines = [str(socat.stderr.readline()), str(socat.stderr.readline())]
    port1 = re.search(r'PTY is (/dev/pts/\d+)', lines[0]).group(1)
    port2 = re.search(r'PTY is (/dev/pts/\d+)', lines[1]).group(1)
    return port1, port2

def spawn_device(device_type):
    """
    Spawn a virtual device of type DEVICE_TYPE.
    """
    port1, port2 = get_virtual_ports()
    fname = os.path.join(os.path.dirname(__file__), "virtual_device.py")
    device = subprocess.Popen(shlex.split("python3 %s -d %s -p %s" % (fname, device_type, port1)))
    POPENS.append(device)
    return port2

@atexit.register
def cleanup():
    """
    Kill all virtual device processes.
    """
    for process in POPENS:
        process.kill()


if __name__ == "__main__":
    VIRTUAL_DEVICE_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "virtual_devices.txt")
    with open(VIRTUAL_DEVICE_CONFIG_FILE, "w+") as device_file:
        DEVICES = [spawn_device(device_type) for device_type in DEVICES_TO_SPAWN]
        device_file.write(" ".join(DEVICES))
    while True:
        time.sleep(1)
