#!/bin/sh

PYTHON_CMD="import json, sys"
PYTHON_CMD="$PYTHON_CMD; assets = json.loads(sys.stdin.read())['assets']"
PYTHON_CMD="$PYTHON_CMD; print([asset['browser_download_url'] for asset in assets if asset['name'].startswith('dawn-linux-x64')][0])"
DAWN_URL=$(curl https://api.github.com/repos/pioneers/PieCentral/releases/latest | python -c "$PYTHON_CMD")

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

wget $DAWN_URL -O ~/Downloads/dawn.zip
sudo unzip ~/Downloads/dawn.zip -d /opt
sudo mv /opt/dawn-linux-x64 /opt/dawn #kinda hacky, but whatever
rm -f ~/Downloads/dawn.zip
