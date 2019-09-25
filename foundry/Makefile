.PHONY: install artifacts-install lint test artifacts

install:
	pip3 install pipenv
	pipenv install --dev

artifacts-install:
	$(nop)

lint:
	cd anvil && vagrant validate
	pipenv run ansible-lint provisioning/*.yml

test:
	$(nop)

artifacts:
	zip -r ../artifacts/foundry.zip *
