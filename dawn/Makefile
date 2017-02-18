dawn-watch:
	npm install && npm run-script watch

dawn-start:
	npm start

install:
	npm install

artifacts-install:
	npm install electron-packager
	sudo dpkg --add-architecture i386
	sudo apt-get update
	sudo apt-get install -y wine
	sudo apt-get install -y p7zip-full

lint:
	npm run-script lint

test:
	npm test

artifacts:
	npm run-script build
	node release.js --platform=win32 --arch=ia32
	node release.js --platform=darwin --arch=x64
	node release.js --platform=linux --arch=x64
	cp ../*.zip ../artifacts
