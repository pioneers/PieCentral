#/bin/bash

#make clean doesn't actually work.  Therefore,

#move to wheverever the flash script is run, 
#and then (as long i've successfuly moved), remove the compiled bin file.
cd `dirname $0` && rm -rf ./bin


python reset.py /dev/ttyACM*
sleep 0.5
python reset.py /dev/ttyACM*
sleep 0.5
python reset.py /dev/ttyACM*
sleep 0.5
# echo "device is:  $1"
# /Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avrdude -C/Users/bduckering/Library/Arduino15/packages/SparkFun/hardware/avr/1.0.3/avrdude.conf -v -patmega32u4 -cavr109 -P/dev/cu.usbmodem1421 -b57600 -D -Uflash:w:"$1":i
# avrdude -v -patmega32u4 -cavr109 -P/dev/ttyACM0 -b57600 -D -Uflash:w:"$1":i

make upload DEVICE=$1
