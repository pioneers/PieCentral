.PHONY: watch start install artifacts-install lint test artifacts

watch: install
	yarn run watch

start:
	yarn start

install:
	yarn install

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
	yarn run pkg --platform=win32 --arch=ia32
	yarn run pkg --platform=darwin --arch=x64
	yarn run pkg --platform=linux --arch=x64
	cp ../*.zip ../artifacts
