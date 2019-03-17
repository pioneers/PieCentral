#!/bin/bash

# Usage: ./DevOps/pipeline/artifacts-pipeline.sh "<app-id>" "<tag>" "<artifacts-dir>"

set -e
pushd DevOps
sudo pip3 install pipenv
pipenv install --dev
pushd pipeline
echo "Deploying artifacts for tag '$2' ..."
pipenv run python pipeline.py -k piecentral-artifacts.pem -a "$1" -t "$2" -d "$3"
popd
popd
