### Build targets for Travis.
.PHONY: install artifacts-install lint test

install:
	cd .. && wget https://downloads.arduino.cc/arduino-1.8.1-linux64.tar.xz
	cd .. && sudo bash setup.sh "arduino-1.8.1-linux64.tar.xz"

artifacts-install:
	$(nop)

lint:
	$(nop)

test:
	cd .. && rm -rf ./bin && make DEVICE=ExampleDevice
