#!/bin/bash

function init-sudo {
  set -e
  cp /etc/sudoers /tmp/sudoers.tmp
  sed -ir 's/%sudo\s+ALL=(ALL:ALL)\s+ALL$/%sudo\s+ALL=(ALL)\s+NOPASSWD:ALL/' /tmp/sudoers.tmp
  visudo -c -f /tmp/sudoers.tmp
  mv -f /tmp/sudoers.tmp /etc/sudoers
}

# Usage: init-user <username> <password> <groups>
function init-user {
  useradd -s /bin/bash -m -G "$3" -p "$2" "$1"
  chpasswd < <(echo "$1:$2")
  updates=/home/"$1"/updates
  mkdir -p "${updates}" && chown "$1:$2" "${updates}"
}

function apt-install {
  apt update -y && apt upgrade -y
  apt install -y $1
  apt clean -y
}

function docker-install {
  curl -sSL https://get.docker.com | sh
}

# Usage: set-hostname <hostname>
function set-hostname {
  old_hostname=$(hostname)
  hostnamectl set-hostname "$1"
  sed -ir "s/${old_hostname}/$1/" /etc/hosts
}

if [ "$(id -u)" != "0" ]; then
	echo "This script should be run as root."
	exit 1
fi

init-sudo
init-user fabric fabric adm,dialout,users,sudo
apt-install build-essential linux-headers-3.10-3-rpi make gcc vim \
            git tmux htop wget
docker-install
set-hostname fabric
