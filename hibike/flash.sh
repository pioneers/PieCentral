#!/bin/bash
set -e

NAME="$0"
SENSOR_TYPES="$(source utils/device_names.sh)"

print_usage() {
    echo "usage: $NAME [-h, --help] SENSOR_TYPE"
    echo "Valid sensors: $SENSOR_TYPES"
    exit 1
}

check_sensor() {
    for sensor in ${SENSOR_TYPES}; do
        if [[ "$1" == "${sensor}" ]]; then
            return 0
        fi
    done
    echo "Invalid sensor type: $1"
    exit 1
}

if (( $# != 1 )); then
    echo "Wrong number of arguments"
    print_usage
    exit 1
fi

# https://stackoverflow.com/questions/12022592/how-can-i-use-long-options-with-the-bash-getopts-builtin#12026302
for arg in "$@"; do
    shift
    case "$arg" in
        "--help") set -- "$@" "-h" ;;
        "--"*) echo "Invalid option"; print_usage ;;
        *) set -- "$@" "$arg" ;;
    esac
done

while getopts ":h" opt; do
    case $opt in
        h) print_usage ;;
        \?) echo "Invalid option"; print_usage ;;
    esac
done

check_sensor $1

#make clean doesn't actually work.  Therefore,
#move to wheverever the flash script is run, 
#and then (as long i've successfuly moved), remove the compiled bin file.
cd "$(dirname "$0")" && rm -rf ./bin

python reset.py /dev/ttyACM*
sleep 0.5
python reset.py /dev/ttyACM*
sleep 0.5
python reset.py /dev/ttyACM*
sleep 0.5
# echo "device is:  $1"
# /Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avrdude -C/Users/bduckering/Library/Arduino15/packages/SparkFun/hardware/avr/1.0.3/avrdude.conf -v -patmega32u4 -cavr109 -P/dev/cu.usbmodem1421 -b57600 -D -Uflash:w:"$1":i
# avrdude -v -patmega32u4 -cavr109 -P/dev/ttyACM0 -b57600 -D -Uflash:w:"$1":i

make upload DEVICE="$1"
