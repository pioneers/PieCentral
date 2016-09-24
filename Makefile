dawn-install:
	cd dawn && npm install

dawn-watch:
	cd dawn && npm install && npm run-script watch

dawn-start:
	cd dawn && npm start

dawn-lint:
	cd dawn && npm run-script lint

dawn-test:
	cd dawn && npm test
