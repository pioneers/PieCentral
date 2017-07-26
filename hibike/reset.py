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
