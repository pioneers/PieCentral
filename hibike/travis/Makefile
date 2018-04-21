# When all devices work, use $(notdir $(wildcard ../devices/*))
DEVICES := BatteryBuzzer ExampleDevice LimitSwitch LineFollower Potentiometer \
	RFID ServoControl YogiBear

.PHONY: install artifacts-install lint test $(DEVICES)

install:
	cd .. && ./setup.sh


artifacts-install:
	$(nop)

lint:
	cd .. && find . -name "*.py" | xargs pylint

unit_tests:
	cd .. && python3 -m unittest hibike_tests/*.py

test: $(DEVICES) unit_tests

$(DEVICES):
	cd .. && $(MAKE) clean-uid DEVICE=$@
	cd .. && $(MAKE) DEVICE=$@
