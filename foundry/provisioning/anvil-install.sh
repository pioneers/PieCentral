#!/bin/bash

set -e

if ! type "vagrant" 2>/dev/null >/dev/null; then
  echo "Error: Unable to find 'vagrant' on your system. Is it installed?"
  exit 1
fi

if ! git rev-parse --git-dir 2>/dev/null >/dev/null; then
  git clone -b master https://github.com/pioneers/PieCentral.git
  cd PieCentral/foundry/provisioning
else
  cd "$(git rev-parse --show-toplevel)/foundry/provisioning"
fi

export MOUNT_SYNCED=no
vagrant up --no-provision
vagrant ssh -c "sudo apt update -y && sudo apt dist-upgrade -y"
vagrant reload --no-provision
vagrant plugin install --local vagrant-vbguest
unset MOUNT_SYNCED
vagrant reload --no-provision
vagrant provision
git remote set-url origin git@github.com:pioneers/PieCentral.git
