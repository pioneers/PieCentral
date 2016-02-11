#/bin/bash

python reset.py /dev/ttyACM*
sleep 3
# echo "device is:  $1"
# /Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avrdude -C/Users/bduckering/Library/Arduino15/packages/SparkFun/hardware/avr/1.0.3/avrdude.conf -v -patmega32u4 -cavr109 -P/dev/cu.usbmodem1421 -b57600 -D -Uflash:w:"$1":i
avrdude -v -patmega32u4 -cavr109 -P/dev/ttyACM* -b57600 -D -Uflash:w:"$1":i

# make upload DEVICE=$1

