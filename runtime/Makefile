.PHONY: build clean install artifacts-install lint test artifacts

USER=pioneers
PROJECT=runtime
NAME=$(USER)/$(PROJECT)
BUILD_FLAGS=

buildbase:
	docker build $(BUILD_FLAGS) --target base -t $(NAME):base .

buildprod:
	docker build $(BUILD_FLAGS) --quiet --target production -t $(NAME):latest --force-rm --pull .

clean:
	docker image rm $(shell docker images --filter="reference=pioneers/runtime:*" -q) --force

export: buildprod
	docker save $(NAME):production | gzip --best > $(PROJECT)-production.tar.gz

run: buildbase
	docker image rm $(shell docker image ls --filter reference=$(NAME):development -q) --force
	docker build --target development -t $(NAME):development .
	docker run --rm -it $(NAME):development

shell:
	docker run --rm -it $(NAME):development /bin/ash

build:
	python setup.py build_ext --inplace

package:
	python setup.py sdist bdist_wheel

#clean:
#	rm -f runtime/*.cpython-*.so runtime/*.c
#	rm -f runtime/packet.cpp runtime/buffer.cpp

install:
	pip3 install pipenv
	pipenv install --dev

artifacts-install:
	$(nop)

lint:
	$(nop)

test:
	pipenv run pytest \
		runtime/journal.py \
		runtime/util.py \
		tests/test_asyncutil.py \
		tests/test_shm.py \
		tests/test_storeservice.py \

artifacts:
	cp ../DevOps/frankfurter/build/*.tar.gz ../artifacts
