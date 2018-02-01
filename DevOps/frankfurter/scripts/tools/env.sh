# env.sh -- A collection of useful variables
#
# To use (from PieCentral):
#   $ source $(git rev-parse --show-toplevel)/DevOps/frankfurter/scripts/tools/env.sh

piecentral=$(git rev-parse --show-toplevel)
runtime="$piecentral/runtime"
hibike="$piecentral/hibike"
frankfurter="$piecentral/DevOps/frankfurter"

user=ubuntu
eth_ip=192.168.6.2
usb_ip=192.168.7.2
if [ -d /tmp ]; then
  tmp_dir=/tmp
else
  tmp_dir=$(pwd)
fi

ifs=%
indent='  '

error="\e[1;31m"    # Bold red
warning="\e[1;33m"  # Bold yellow
success="\e[1;32m"  # Bold green
clear="\e[0m"

alias ssh='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -t'
