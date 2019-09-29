.PHONY: install artifacts-install lint test artifacts

install:
	pip3 install pipenv
	pipenv install --dev

artifacts-install:
	$(nop)

lint:
	pipenv run ansible-lint provisioning/*.yml

test:
	$(nop)

artifacts:
	zip -r ../artifacts/foundry.zip *
