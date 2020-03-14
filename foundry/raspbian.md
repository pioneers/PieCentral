# Raspbian Provisioning

The robot is controlled by a [Raspberry Pi](https://www.raspberrypi.org/), a single-board computer (SBC) running a variant of Debian Linux called Raspbian.
PiE builds a customized operating system off of Raspbian to support our robotics competition.
In particular,
1. The Pi must start Runtime on boot.
1. The Pi must be able to update itself (typically the Runtime source and system configuration files).
1. The Pi must accept student code.

## Writing the Base Image

Before you begin, you should be aware that building the base image only needs to be done once every season.
During deployment, a single base image is cloned across multiple microSD cards.
Afterwards, team-specific configuration (*i.e.*, router pairing) and integration testing is performed for each Pi individually.

The procedure for generating the base image exists for the sake of reproducibility.

Download the [latest Raspbian Lite image](https://downloads.raspberrypi.org/raspbian_lite_latest).
At the time of this writing, this image was:
```
Release date: 2020-02-13
Kernel version: 4.19
SHA-256: 12ae6e17bf95b6ba83beca61e7394e7411b45eba7e6a520f434b0748ea7370e8
```

Using a app like [Etcher](https://www.balena.io/etcher/), flash this image to a microSD card.
This will create two partitions named `boot` and `rootfs`.
Alternatively, use the `dd` utility like so (check the intended output `of` with `lsblk`):
```bash
$ dd status=progress if=2020-02-13-raspbian-buster-lite.img of=/dev/mmcblk0 bs=32M conv=fsync
```
Writing to storage probably requires `sudo`.

## Basic Configuration

Insert the flashed card into a Raspberry Pi, attach a keyboard and monitor to the Pi, then power the Pi with a 5V 2A micro-USB power supply.
You should see the Pi boot.
Log in as the default user `pi` with password `raspberry`.

Run `sudo raspi-config`, then select the following options.

```
Network Options > Wi-Fi > United States > [SSID, such as "CalVisitor"] > [password, if necessary]
Network Options > Network interface names > Yes
Boot Options > Desktop / CLI > Console
Boot Options > Wait for Network at Boot > No
Localisation Options > Change Locale > en_US.UTF-8 UTF-8 (disable en_GB.UTF-8 UTF-8) > en_US.UTF-8.UTF-8
Localisation Options > Change Keyboard Layout > Logitech > Other > English (US) > The default for the keyboard layout > No compose key
Interfacing Options > [SSH, Serial] > Yes
Interfacing Options > [everything else] > No
Advanced Options > Expand Filesystem
```

Select `Finish` from the main menu, then reboot.

## Bootstrap Installation

Connect your laptop to the Pi over Ethernet (you may need a Ethernet-to-USB adapter).
On the Pi, log in again as `pi` and `raspberry`.
Run `ip a` to confirm the `eth0` network interface is available, then assign the Pi an Ethernet address:
```sh
pi@raspberrypi:~ $ sudo ip a add 192.168.1.2/24 dev eth0
```

On your laptop, assign the Ethernet interface an IP address (such as `192.168.1.1`) similarly:
```sh
$ sudo ip a add 192.168.1.1/24 dev eth0
```

If you were unable to connect to Wifi using `raspi-config`, you can run the interactive `netbridge.sh` script (possibly with `sudo`) to set up forwarding through your laptop's wifi.
The interface the laptop accepts from is the Ethernet interface shared with the Pi, and the interface the laptop forwards to is typically Wifi.
The remote IP is the Pi's IP (in the example above, `192.168.1.2`), and the user to log in as is `pi`.

Now, if you run `ping 8.8.8.8` or `ping 192.168.1.1` on the Pi, you should not see any lost packets.
Also, you should now be able to SSH into the Pi over Ethernet.
```sh
$ ssh pi@192.168.1.2
```

### Running the Playbook

To set up a base image, run:

```sh
$ ansible-playbook provisioning/raspbian.yml \
  --inventory=192.168.1.2, \
  --extra-vars="datetime='$(date)'"
```

The `--check` and `--list-tasks` flags are helpful for performing a dry-run.
`--start-at-task="<task>"` can be used for redriving failed tasks.

You can use a disk editor like GParted to shrink the size of the base card's partition down to a more reasonable size for cloning (about 3GB instead of the entire size of the card).
Then, use `raspi-config` during the team configuration stage to re-expand the cloned card.

To read the card image (probably requires `sudo` as well):
```sh
$ dd status=progress if=/dev/mmcblk0 of=$(date +%Y-%m-%d)-foundry-raspbian.img bs=32M count=<count>
```
To determine how many blocks of size `bs` to ready, run `fdisk -l` to find the end of the last partition, add one, multiply by the sector size (typically 512 bytes) to get the size of the segment to clone in bytes, divide by your chosen block size, then round up.
For example:
```python
>>> from math import ceil
>>> int(ceil(512*(7129087+1)/(32*1024*1024)))  # bs=32M
```

## Router Pairing

Connect to the Pi over SSH, as before.
To extend the base image for a particular team, run:

```sh
$ ansible-playbook provisioning/raspbian.yml \
  --tags=team \
  --inventory=192.168.1.2, \
  --extra-vars "team_number=** team_psk=********"
```

## Router Setup

Run `ip a` to determine the MAC address of the Pi's wireless interface `wlan0`, and record this MAC address in a deployment log (*e.g.*, a Google spreadsheet).
Power the router, add the router password to the log, change the SSID to `Team**`, where `**` stands for the two-digit team number, and add a static ARP reservation mapping the MAC address to `192.168.0.2`.

## Integration Testing

From `runtime`, run `./package.sh` to generate the latest build of Runtime.
Run the interactive validation playbook, connecting to SSH as before:
```sh
$ export RUNTIME_DIR=$(git rev-parse --show-toplevel)/runtime
$ ansible-playbook validation/raspbian.yml \
  --inventory=192.168.1.2, \
  --extra-vars="{
    'team_number': **,
    'update': '$(echo $RUNTIME_DIR/runtime-*.tar.gz | sort -r | head)',
    'student_code': '$RUNTIME_DIR/studentcode.py'
  }"
```
This playbook checks:
* Whether `systemd` runs Runtime
* Whether Runtime can be updated
* Whether SSH is consistently enabled after multiple reboots
* Whether student code uploads are committed.

Connecting your laptop to the `Team**` router, check whether Dawn connects to `192.168.0.2`.

Label both the Pi enclosure and router box with a sticker with the team number written on it.

## References

1. [`systemd` manuals](https://www.freedesktop.org/software/systemd/man/)
1. [`ansible` concepts](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html)
1. [`ansible` modules](https://docs.ansible.com/ansible/latest/modules/modules_by_category.html#modules-by-category)
