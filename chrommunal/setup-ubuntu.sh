#!/bin/sh

declare -a APT_PACKAGES=(
  arduino
  arduino-core
  arduino-mk
  avr-libc
  avrdude
  build-essential
  git
  htop
  make
  net-tools
  python
  python-dev
  python-pip
  python3
  python3-dev
  python3-pip
  tmux
  vim
)

declare -a PIP_PACKAGES=(
  pyserial
)

for package in "${APT_PACKAGES[@]}"
do
  sudo apt-get install -y $package
done

for package in "${PIP_PACKAGES[@]}"
do
  sudo pip2 install --upgrade $package
  sudo pip3 install --upgrade $package
done

# TODO(vincent): download and install dawn in /opt/...
#                currently blocked by pioneers.github.io/dawn not having a linux build...merp
# wget <Link to dawn> -O ~/Downloads/dawn.tar.gz
# tar -xzvf ~/Downloads/dawn.tar.gz /opt/dawn
