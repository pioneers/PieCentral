.PHONY: watch start install artifacts-install lint test artifacts

watch: install
	yarn run watch

start:
	yarn start

install:
	yarn install --frozen-lockfile

artifacts-install:
	yarn add --no-lockfile electron-packager
	sudo dpkg --add-architecture i386
	sudo apt-get update
	sudo apt-get install -y wine
	sudo apt-get install -y p7zip-full

lint:
	yarn run lint

test:
	yarn test

artifacts:
	yarn run build
	node release.js --platform=win32 --arch=ia32
	node release.js --platform=darwin --arch=x64
	node release.js --platform=linux --arch=x64
	cp ../*.zip ../artifacts
