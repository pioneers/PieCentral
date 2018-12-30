.PHONY: build clean install artifacts-install lint test artifacts

build:
	python setup.py build_ext --inplace

package:
	python setup.py sdist bdist_wheel

clean:
	rm -f runtime/*.cpython-*.so runtime/*.c
	rm -f runtime/packet.cpp runtime/buffer.cpp

install:
	cd build-deps && wget https://github.com/google/protobuf/releases/download/v3.2.0/protoc-3.2.0-linux-x86_64.zip
	cd build-deps && unzip protoc-3.2.0-linux-x86_64.zip
	pip3 install pipenv
	pipenv install --dev

artifacts-install:
	$(nop)

lint:
	pylint runtime/statemanager.py
#	pylint --load-plugins=$(shell pwd)/lints ansible.py runtime.py statemanager.py studentapi.py runtimeUtil.py fakedawn.py hibikesimulator.py

test:
	pipenv run pytest \
		runtime/journal.py \
		runtime/util.py \
		tests/test_asyncutil.py \
		tests/test_shm.py \
		tests/test_storeservice.py \

# 	tests/test_executor.py
#	cd ../DevOps/frankfurter/scripts/update && ./create_update -p

artifacts:
	cp ../DevOps/frankfurter/build/*.tar.gz ../artifacts
