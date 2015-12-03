#/bin/bash

echo Putting smartsensor into reset mode
echo
screen -D -m -S 'reset' /dev/ttyACM1 1200 &
sleep 0.5
screen -X -S reset quit
sleep 1


echo
echo Programming smartsensor
# /Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avrdude -C/Users/bduckering/Library/Arduino15/packages/SparkFun/hardware/avr/1.0.3/avrdude.conf -v -patmega32u4 -cavr109 -P/dev/cu.usbmodem1421 -b57600 -D -Uflash:w:"$1":i
make upload
