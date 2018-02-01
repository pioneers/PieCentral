#!/bin/bash
# THIS FILE ASSUMES YOU HAVE HOMEBREW AND X-CODE INSTALLED ON YOUR MAC.

if [[ "$(id -u)" == "0" ]]; then
    echo "Please run without sudo permissions."
    exit 1
fi

deps=("make" "gcc" "gcc-avr" "arduino-mk" "python3-pip")

if ! type make >/dev/null 2>&1 || ! type gcc >/dev/null 2>&1; then 
	echo "Install x-code on your mac!"
	exit 1
fi

if ! type avr-gcc >/dev/null 2>&1; then
	echo "Installing avr-gcc: Warning, install will take a long time."
	brew tap osx-cross/avr
	brew install avr-gcc
fi

if [[ $(brew list | grep -c arduino-mk) == 0 ]]; then
        echo" Installing arduino-mk: Warning, install will take a long time."
	# add tap
	brew tap sudar/arduino-mk
	# to install the last stable release
	brew install arduino-mk
	# to install the development version
	brew install --HEAD arduino-mk
fi

if ! type pip3 >/dev/null 2>&1; then
	brew install python3
fi


if ! command -v pipenv &> /dev/null; then
    pip3 install pipenv
fi

pipenv install --dev
pip3 install serial
echo "All dependencies installed."

echo "Next steps: download Arduino 1.8.1 (should have Arduino.app in Applications folder), python should map to python3 or you will get an error."

echo "  ARDUINO_DIR   = /Applications/Arduino.app/Contents/Java
  AVR_TOOLS_DIR = \${ARDUINO_DIR}/hardware/tools/avr
  AVRDUDE_CONF  = \$(AVR_TOOLS_DIR)/etc/avrdude.conf
  AVRDUDE = \${AVR_TOOLS_DIR}/bin/avrdude
  MONITOR_PORT = /dev/tty.usbmodem*
" |cat - Arduino-Makefile/Arduino.mk > /tmp/out && mv /tmp/out Arduino-Makefile/Arduino.mk

