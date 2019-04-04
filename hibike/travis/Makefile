# When all devices work, use $(notdir $(wildcard ../devices/*))
DEVICES := BatteryBuzzer ExampleDevice LimitSwitch LineFollower Potentiometer \
	RFID ServoControl PolarBear

.PHONY: install artifacts-install lint test $(DEVICES)

install:
	cd .. && ./setup.sh

artifacts-install:
	$(nop)

lint:
	cd .. && find . -type d -name "hibike_packet_extension" -prune -o -type f -name "*.py" -print | xargs pylint

unit_tests:
	cd .. && pipenv run python -m unittest hibike_tests/*.py

test: $(DEVICES) unit_tests

$(DEVICES):
	cd .. && $(MAKE) clean-uid DEVICE=$@
	cd .. && $(MAKE) DEVICE=$@
