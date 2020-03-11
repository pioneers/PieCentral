#!/bin/bash

# package.sh -- Package runtime as a standalone distribution

set -e
pipenv run python3 setup.py sdist bdist_wheel
pipenv lock --requirements > dist/requirements.txt
pipenv run pip download --platform linux_armv7 --no-deps -r dist/requirements.txt --dest dist
rm dist/requirements.txt
cp -r ../foundry/update/* dist
zip -r runtime-$(date --utc +%F-%H-%M-%S).zip dist
