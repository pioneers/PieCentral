#!/usr/bin/env python

import serial, time, sys

def reset(device):
  ''' The Caterina bootloader goes into reset mode for 8 seconds when a serial
  connection is made at 1200 baud and disconnected. '''
  with serial.Serial(device, baudrate=1200) as conn:
    conn.setDTR(False)  # Needed on Ubuntu but not Mac
    conn.close()


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print 'Usage: $ python reset.py /dev/<device>'
    sys.exit()

  dev = sys.argv[1]

  try:
    reset(dev)
    print 'Successfully reset device'
  except None:
    pass

# Usage: $python reset.py /dev/ttyACM* && sleep 3 && make upload DEVICE=<smardevice>