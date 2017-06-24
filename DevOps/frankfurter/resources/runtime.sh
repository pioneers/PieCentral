#!/bin/bash

cd /home/ubuntu/PieCentral/runtime
export PYTHONPATH=/home/ubuntu/PieCentral/hibike:/home/ubuntu/PieCentral/runtime
exec python3 runtime.py
