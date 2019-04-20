# fabric
Fabric is the latest iteration of the PiE kit operating system image.
In year 11 (Spring 2019), PiE transitioned from using the Beaglebone Black (BBB) as its kit single-board computer (SBC) to the Raspberry Pi 3B+.
The Raspberry Pi offers several advantages over the Beaglebone:
* The Pi's ARM Cortex-A53 has four physical cores (up from the single core on the BBB's ARM Cortex-A8) yielding increased parallelism and better performance.
  The time-to-boot was also greatly reduced.
* The Pi loads its disk from a removable microSD card, which can be swapped easily to patch critical issues.
* The Pi has on-board WiFi, which cannot be dislodged by mechanical shocks.
  This also eliminates the need to purchase WiFi dongles and build the associated drivers.
* The Pi community is more active, with better documentation and support.

## Building the Fabric Base Image

Before you begin, you should be aware that building the base image need only be done once every season.
During deployment, a single base image is cloned across multiple microSD cards.
This procedure exists only for the sake of reproducibility.

Download the [latest Raspbian Lite image](https://downloads.raspberrypi.org/raspbian_lite_latest).
At the time of this writing, this image was:
```
Release date: 2019-04-08
Kernel version: 4.14
SHA-256: a3ced697ca0481bb0ab3b1bd42c93eb24de6264f4b70ea0f7b6ecd74b33d83eb
```

Using a app like [Etcher](https://www.balena.io/etcher/), burn this image to a microSD card.
This will create two partitions named `boot` and `rootfs`.
```bash
$ touch /path/to/boot/ssh
$ cp /path/to/fabric/wpa_supplicant.conf /path/to/boot
```

### Basic Configuration

Insert the flashed card into a Raspberry Pi, attach a keyboard and monitor to the Pi, then power the Pi with a 5V 2A micro-USB power supply.
You should see the Pi boot (there will be Pi logos in the monitor's upper left-hand corner).
Log in as the default user `pi` with password `raspberry`.

Run `sudo raspi-config`, then select the following options.

```
Boot Options > Desktop / CLI > Console
Boot Options > Wait for Network at Boot > No
Localisation Options > Change Locale > en_US.UTF-8 UTF-8 (disable en_GB.UTF-8 UTF-8) > en_US.UTF-8.UTF-8
Localisation Options > Change Timezone > America > Los_Angeles
Localisation Options > Change Keyboard Layout > Logitech Generic Keyboard > Other > English (US) > The default for the keyboard layout > No compose key
Interfacing Options > Camera > No
Interfacing Options > SSH > Yes
Interfacing Options > VNC > No
Interfacing Options > SPI > No
Interfacing Options > I2C > No
Interfacing Options > Serial > Yes
Interfacing Options > 1-Wire > No
Interfacing Options > Remote GPIO > No
Advanced Options > Expand Filesystem
```

Finish, then reboot.

### Setting Up the Network Bridge

You will need a **host machine** running Linux to give the Pi access to the internet.
Connect the host to the Pi over Ethernet (you may need a Ethernet-to-USB adapter).
On the Pi, log in again as `pi` and `raspberry`.
Run `ip a` to confirm the `eth0` network interface is available, then assign the Pi an Ethernet address:
```sh
pi@raspberrypi:~ $ sudo ip a add 192.168.0.2/24 dev eth0
pi@raspberrypi:~ $ sudo ip route add default via 192.168.0.1
```

On the host machine, assign the Ethernet interface the gateway IP address (in the example above, `192.168.0.1`):
```sh
$ sudo ifconfig enp0s20f0u2 192.168.0.1
```

Once connected, run the interactive `netbridge.sh` script (possibly with `sudo`) to set up forwarding.
The interface the host accepts from is the Ethernet interface shared with the Pi, and the interface the host forwards to is typically Wi-Fi.
The remote IP is the Pi's IP (in the example above, `192.168.0.2`), and the user to log in as is `pi`.
Now, if you run `ping 8.8.8.8` on the Pi, you should not see any lost packets.

### Running Runtime

Copy `fabric/fabricsetup.sh` to the Pi.
```sh
$ scp fabricsetup.sh pi@192.168.0.2:~
```

On the Pi,
```sh
pi@raspberrypi:~ $ sudo ./fabricsetup.sh
pi@raspberrypi:~ $ sudo reboot
```

Once the Pi reboots, on the host, copy over these configuration files to the Pi (you may have to re-set the Pi's IP address):
```sh
$ scp dhcpcd.conf fabric@192.168.0.2:~
$ scp -r bin fabric@192.168.0.2:~
$ scp -r systemd-units fabric@192.168.0.2:~
$ scp bashrc fabric@192.168.0.2:~/.bashrc
```

Now, log in as `fabric` with password `fabric`, and run:
```sh
fabric@fabric:~ $ sudo userdel -rf pi
fabric@fabric:~ $ mkdir -p updates .local
fabric@fabric:~ $ chmod +x bin/* && mv bin .local
fabric@fabric:~ $ sudo mv systemd-units/* /etc/systemd/system
fabric@fabric:~ $ sudo systemctl enable fabric-update.service
fabric@fabric:~ $ sudo systemctl enable fabric-update.path
fabric@fabric:~ $ sudo systemctl enable fabric-start.service
fabric@fabric:~ $ sudo systemctl daemon-reload
fabric@fabric:~ $ rmdir systemd-units
fabric@fabric:~ $ sudo mv dhcpcd.conf /etc
```
