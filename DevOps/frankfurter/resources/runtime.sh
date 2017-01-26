#!/bin/bash

# Place into `/etc/init.d`, run `sudo chmod +x runtime` on it, and
# run `update-rc.d runtime`

bash /home/ubuntu/updates/update.sh || true
cd /home/ubuntu/PieCentral/runtime/testy
export PYTHONPATH=/home/ubuntu/PieCentral/hibike:/home/ubuntu/PieCentral/runtime/testy
exec python3 runtime.py
