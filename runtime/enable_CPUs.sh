#!/bin/bash
#ask for root access
[ "$(whoami)" != "root" ] && exec sudo -- "$0" "$@"

for x in /sys/devices/system/cpu/cpu*/online; do
	echo 1 >"$x";
done
echo "DONE"
