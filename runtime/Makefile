.PHONY: install artifacts-install lint test artifacts

export PYTHONPATH := $(PYTHONPATH):$(shell realpath .)

install:
	cd build-deps && wget https://github.com/protocolbuffers/protobuf/releases/download/v3.5.1/protoc-3.5.1-linux-aarch_64.zip
	cd build-deps && unzip protoc-3.5.1-linux-aarch_64.zip
	pip3 install pipenv
	pipenv install --dev

artifacts-install:
	$(nop)

lint:
	pylint --exit-zero runtime/ansible.py runtime/__main__.py runtime/util.py runtime/studentapi.py runtime/statemanager.py fakedawn.py hibikesimulator.py

test:
	protoc -I=../ansible-protos --python_out=runtime ../ansible-protos/*.proto
	python3 -m runtime --test
	python3 -m runtime --test optionalTestsWork

artifacts:
	./package.sh && mv *.tar.gz ../artifacts

clean:
	rm -rf build dist runtime.egg-info
