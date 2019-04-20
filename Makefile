.PHONY: build

TAR=fabric-latest.tar
TAG=pioneers/fabric
TARGET_SHELL=/bin/ash

build:
	docker build --platform=linux/arm/v7 -t $(TAG):latest .
	docker save $(TAG) > $(TAR)
	gzip $(TAR)

run:
	docker run --name=runtime --net=host --rm -it --privileged \
						 -v studentcode:/root/runtime/studentCode.py $(TAG):latest

shell:
	docker run --name=runtime --net=host --rm -it $(TAG) $(TARGET_SHELL)

all:

clean:
	docker image rm -f $(TAG):latest
