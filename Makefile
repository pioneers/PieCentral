.PHONY: build

TAR=fabric-latest.tar
TAG=pioneers/fabric
TARGET_SHELL=/bin/ash

build:
	docker build --platform=linux/arm/v7 -t $(TAG):latest .
	docker save $(TAG) > $(TAR)
	gzip $(TAR)

run:
	docker run --rm -it --privileged \
						 -p 1234-1236:1234-1236 -p 6020:6020 \
						 -v studentcode:/root/runtime/studentCode.py $(TAG):latest

shell:
	docker run --rm -it $(TAG) $(TARGET_SHELL)

all:

clean:
	docker image rm -f $(TAG):latest
