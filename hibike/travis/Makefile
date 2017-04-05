DEVICES := $(notdir $(wildcard ../devices/*))

.PHONY: install artifacts-install lint test $(DEVICES)

install:
	cd .. && wget https://downloads.arduino.cc/arduino-1.8.1-linux64.tar.xz
	cd .. && sudo bash setup.sh "arduino-1.8.1-linux64.tar.xz"

artifacts-install:
	$(nop)

lint:
	$(nop)

test: $(DEVICES)

$(DEVICES):
	cd .. && rm -rf ./bin
	cd .. && make DEVICE=$@
