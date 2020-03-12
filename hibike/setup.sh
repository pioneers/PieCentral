#!/bin/bash

sudo ./sudo_setup.sh

if ! command -v pipenv &> /dev/null; then
    pip3 install pipenv
fi

pipenv install --dev
echo "All dependencies installed."
