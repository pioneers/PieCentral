.PHONY: install artifacts-install lint test artifacts

install:
	pip3 install pipenv
	pipenv install --dev

artifacts-install:
	$(nop)

lint:
#	ansible-lint

test:
	cd anvil && vagrant validate
	# TODO: validate playbooks

artifacts:
	cp -r anvil provisioning README.md ../artifacts
