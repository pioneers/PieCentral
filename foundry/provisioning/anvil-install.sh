#!/bin/bash

set -e

if ! type "vagrant" 2>/dev/null >/dev/null; then
  echo "Error: Unable to find 'vagrant' on your system. Is it installed?"
  exit 1
fi

if ! git rev-parse --git-dir 2>/dev/null >/dev/null; then
  git clone -b master https://github.com/pioneers/PieCentral.git
  cd PieCentral/foundry/provisioning
fi

export MOUNT_SYNCED=no
vagrant up --no-provision
vagrant ssh -c "sudo apt update -y && sudo apt dist-upgrade -y"
vagrant reload
vagrant plugin install --local vagrant-vbguest
unset MOUNT_SYNCED
vagrant provision
vagrant reload

echo "Setup completed successfully! Please copy the SSH key below and follow these instructions: "
echo "  https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account."
echo
vagrant ssh -c "cat .ssh/id_rsa.pub"
echo
echo "You can now log into your development environment using 'vagrant ssh'."

git remote set-url origin git@github.com:pioneers/PieCentral.git
