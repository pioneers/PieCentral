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
Download the [latest Raspbian Lite image](https://downloads.raspberrypi.org/raspbian_lite_latest).
At the time of this writing, this image was:
```
Release date: 2018-11-13
Kernel version: 4.14
SHA-256: 47ef1b2501d0e5002675a50b6868074e693f78829822eef64f3878487953234d
```
Using a app like [Etcher](https://www.balena.io/etcher/), burn this image to a microSD card.
This will create two partitions named `boot` and `rootfs`.
```bash
$ touch /path/to/boot/ssh
$ cp /path/to/fabric/wpa_supplicant.conf /path/to/boot
```

### Networking

### Raspi

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
Interfacing Options > Advanced Options > Expand Filesystem
```

Finish, then reboot.
