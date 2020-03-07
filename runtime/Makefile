.PHONY: build-dev-image build-prod-image clean install artifacts-install lint test artifacts

USER=pioneers
PROJECT=runtime
NAME=$(USER)/$(PROJECT)
BUILD_FLAGS=

build-dev-image:
	docker build $(BUILD_FLAGS) --target development -t $(NAME):development .

build-prod-image:
	docker build $(BUILD_FLAGS) --quiet --target production -t $(NAME):latest --force-rm --pull .

clean:
	docker image rm $(shell docker images --filter="reference=pioneers/runtime:*" -q) --force

shell: build-dev-image
	docker run --rm -it $(NAME):development /bin/ash

install: build-dev-image

artifacts-install:
	$(nop)

lint: install
	docker run --rm -it $(NAME):development /usr/bin/env pipenv run lint

test: install
	docker run --rm -it $(NAME):development /usr/bin/env pipenv run test

artifacts: build-prod-image
	docker save $(NAME):production | gzip --best > ../artifacts/$(PROJECT)-production.tar.gz
