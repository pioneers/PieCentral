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
#!/usr/bin/env python
"""
Reset code for flashing Arduinos.
"""
import sys
# pylint: disable=import-error
import serial


def reset(device):
    ''' The Caterina bootloader goes into reset mode for 8 seconds when a serial
    connection is made at 1200 baud and disconnected. '''
    with serial.Serial(device, baudrate=1200) as conn:
        conn.setDTR(False)  # Needed on Ubuntu but not Mac
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: $ python reset.py /dev/<device>')
        sys.exit()

    DEVICE = sys.argv[1]

    try:
        reset(DEVICE)
        print('Successfully reset device')
    except serial.SerialException:
        pass

# Usage: $python reset.py /dev/ttyACM* && sleep 3 && make upload DEVICE=<smardevice>
