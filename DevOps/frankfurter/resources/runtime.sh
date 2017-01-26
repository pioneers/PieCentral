#!/bin/bash

cd /home/ubuntu/PieCentral/runtime/testy
export PYTHONPATH=/home/ubuntu/PieCentral/hibike:/home/ubuntu/PieCentral/runtime/testy
exec python3 runtime.py
