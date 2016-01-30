#/bin/bash

python reset.py /dev/ttyACM*
sleep 3
echo "device is:  $1"

make upload DEVICE=$1