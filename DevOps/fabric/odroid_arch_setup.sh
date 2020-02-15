#!/bin/bash

# Give the current user sudo privileges (no password).
function sudo-init {
  echo "$1" | su root -c "
    set -e
    cp /etc/sudoers /tmp/sudoers.tmp
    sed -ir 's/^# %wheel ALL=(ALL) NOPASSWD: ALL$/%wheel ALL=(ALL) NOPASSWD: ALL/g' /tmp/sudoers.tmp
    diff --color /etc/sudoers /tmp/sudoers.tmp
    visudo -c -f /tmp/sudoers.tmp
    mv -f /tmp/sudoers.tmp /etc/sudoers
    usermod -aG wheel $(whoami)
  " 2> /dev/null
  echo "'$(whoami)' has been added to the 'wheel' group."
}

function systemd-init {
  $sudo timedatectl set-timezone "$1"
  echo "The time is: $(date)"
  $sudo whoami
}

# Initialize the pacman keyring, install core packages,
# and install yay (the AUR helper).
function pacman-init-install {
  $sudo pacman-key --init
  $sudo pacman-key --populate archlinuxarm
  $sudo pacman --noconfirm -Syu
  $sudo pacman --noconfirm -S $@
  $sudo sudo acman --noconfirm -Scc
  git clone https://aur.archlinux.org/yay.git
  cd yay && makepkg --noconfirm -si && cd .. && rm -rf yay
}

# Set to 'sudo' to run commands as root,
# or empty to run as the current user.
sudo=sudo

set -e
sudo-init root  # Default root password
systemd-init America/Los_Angeles
sudo pacman-init-install make binutils gcc sudo fakeroot \
  go vim git tmux htop wavemon wget docker \
  python3 python-pip

echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
pip install --user pipenv
git clone https://github.com/pioneers/PieCentral.git
cd PieCentral/runtime
pipenv install
