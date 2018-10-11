#!/bin/bash

# Usage: bash DevOps/pipeline/artifacts-pipeline.sh "$APP_ID" "$TRAVIS_TAG"

pushd DevOps
pipenv install --dev
pushd pipeline
pipenv run python3 pipeline.py -k piecentral-artifacts.pem -a "$1" -t "$2" -d "$3"
popd
popd
