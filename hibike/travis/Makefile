# When all devices work, use $(notdir $(wildcard ../devices/*))
DEVICES := BatteryBuzzer ExampleDevice LimitSwitch LineFollower Potentiometer \
	RFID ServoControl TeamFlag YogiBear

.PHONY: install artifacts-install lint test $(DEVICES)

install:
	cd .. && ./setup.sh

artifacts-install:
	$(nop)

lint:
	cd .. && find . -name "*.py" | xargs pylint

test: $(DEVICES)

$(DEVICES):
	cd .. && $(RM) -r ./bin
	cd .. && $(MAKE) DEVICE=$@
