.PHONY: install artifacts-install lint test artifacts

install:
	cd ../build-deps && wget https://github.com/google/protobuf/releases/download/v3.2.0/protoc-3.2.0-linux-x86_64.zip
	cd ../build-deps && unzip protoc-3.2.0-linux-x86_64.zip
	pip3 install protobuf

artifacts-install:
	$(nop)

lint:
	$(nop)

test:
	cd ../DevOps/frankfurter/scripts/update && ./create_update.sh
	protoc -I=../ansible-protos --python_out=testy ../ansible-protos/*.proto
	cd testy && python3 runtime.py --test

artifacts:
	cp ../DevOps/frankfurter/build/*.tar.gz ../artifacts
