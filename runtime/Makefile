.PHONY: build clean install artifacts-install lint test artifacts

USER=pioneers
PROJECT=runtime
NAME=$(USER)/$(PROJECT)
BUILD_FLAGS=

buildbase:
	docker build $(BUILD_FLAGS) --target base -t $(NAME):base .

builddev:
	docker build --target development -t $(NAME):development .

buildprod:
	docker build $(BUILD_FLAGS) --quiet --target production -t $(NAME):latest --force-rm --pull .

clean:
	docker image rm $(shell docker images --filter="reference=pioneers/runtime:*" -q) --force

export: buildprod
	docker save $(NAME):production | gzip --best > $(PROJECT)-production.tar.gz

run: builddev
	docker run --rm -it $(NAME):development

runprod: builddev
	docker run --restart=always --rm -it $(NAME):development /usr/bin/env pipenv run python3 -m runtime run

shell: buildbase
	docker run --rm -it $(NAME):development /bin/ash

package:
	python setup.py sdist bdist_wheel

build:
	pipenv run build

clean:
	find runtime \( -name '*.cpython-*.so' -o -name '*.c' -o -name '*.cpp' \) -delete
	rm -rf build dist

install:
	pip3 install pipenv
	pipenv install --dev --pre
	pipenv run build

artifacts-install:
	$(nop)

lint:
	pipenv run lint

test:
	pipenv run test

testcontainer:
	docker run --rm -it $(NAME):development python3 -m doctest \
		runtime/util/exception.py \
		runtime/service/device.py

artifacts:
