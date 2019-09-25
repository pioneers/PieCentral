#!/bin/bash

set -e

if ! type "vagrant" 2>/dev/null >/dev/null; then
  echo "Error: Unable to find 'vagrant' on your system. Is it installed?"
  exit 1
fi

if ! git rev-parse --git-dir 2>/dev/null >/dev/null; then
  git clone -b master git@github.com:pioneers/PieCentral.git
  cd PieCentral/foundry/anvil
fi

export MOUNT_SYNCED=no
vagrant up
unset MOUNT_SYNCED
vagrant plugin install --local vagrant-vbguest
vagrant reload

echo "Setup completed successfully! Please copy the SSH key below and follow these instructions: "
echo "  https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account."
vagrant ssh -c "cat .ssh/id_rsa.pub"
echo "You can now log into your development environment using 'vagrant ssh'."
