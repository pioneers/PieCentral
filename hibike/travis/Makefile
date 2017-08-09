# When all devices work, use $(notdir $(wildcard ../devices/*))
DEVICES := BatteryBuzzer ExampleDevice LimitSwitch LineFollower Potentiometer \
	RFID ServoControl TeamFlag YogiBear

.PHONY: install artifacts-install lint test $(DEVICES)

install:
	cd .. && wget https://downloads.arduino.cc/arduino-1.8.1-linux64.tar.xz
	cd .. && sudo bash setup.sh "arduino-1.8.1-linux64.tar.xz"

artifacts-install:
	$(nop)

lint:
	cd .. && find . -name "*.py" | xargs pylint

test: $(DEVICES)

$(DEVICES):
	cd .. && rm -rf ./bin
	cd .. && make DEVICE=$@
