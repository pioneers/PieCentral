#!/bin/bash

# Usage: bash DevOps/pipeline/artifacts-pipeline.sh "<app-id>" "<tag>" "<artifacts-dir>"

set -e
pushd DevOps
pip3 install --user pipenv
pipenv install --dev
pushd pipeline
echo "Deploying artifacts for '$TRAVIS_TAG' ..."
pipenv run python3 pipeline.py -k piecentral-artifacts.pem -a "$1" -t "$2" -d "$3"
popd
popd
