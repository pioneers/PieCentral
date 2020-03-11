# Raspbian Provisioning

## Building the Fabric Base Image

Before you begin, you should be aware that building the base image need only be done once every season.
During deployment, a single base image is cloned across multiple microSD cards.
This procedure exists only for the sake of reproducibility.

Download the [latest Raspbian Lite image](https://downloads.raspberrypi.org/raspbian_lite_latest).
At the time of this writing, this image was:
```
Release date: 2020-02-13
Kernel version: 4.19
SHA-256: 12ae6e17bf95b6ba83beca61e7394e7411b45eba7e6a520f434b0748ea7370e8
```

Using a app like [Etcher](https://www.balena.io/etcher/), burn this image to a microSD card.
This will create two partitions named `boot` and `rootfs`.
Alternatively, use the `dd` utility like so:
```bash
$ dd status=progress if=2020-02-13-raspbian-buster-lite.img of=/dev/mmcblk0 bs=4M conv=fsync
```

### Basic Configuration

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

### Setting Up Networking

Connect your laptop to the Pi over Ethernet (you may need a Ethernet-to-USB adapter).
On the Pi, log in again as `pi` and `raspberry`.
Run `ip a` to confirm the `eth0` network interface is available, then assign the Pi an Ethernet address:
```sh
pi@raspberrypi:~ $ sudo ip a add 192.168.0.2/24 dev eth0
```

On your laptop, assign the Ethernet interface the gateway IP address (in the example above, `192.168.0.1`) similarly:
```sh
$ sudo ip a add 192.168.0.1/24 dev eth0
```

If you were unable to connect to Wifi using `raspi-config`, you can run the interactive `netbridge.sh` script (possibly with `sudo`) to set up forwarding through your laptop's wifi.
The interface the laptop accepts from is the Ethernet interface shared with the Pi, and the interface the laptop forwards to is typically Wifi.
The remote IP is the Pi's IP (in the example above, `192.168.0.2`), and the user to log in as is `pi`.

Now, if you run `ping 8.8.8.8` on the Pi, you should not see any lost packets.
Also, you should now be able to SSH into the Pi over Ethernet.
```sh
$ ssh pi@192.168.0.2
```

### Running the Playbook

```sh
$ ansible-playbook provisioning/raspbian.yml \
  --inventory=192.168.0.2, \
  --extra-vars="datetime='$(date)'"
$ ansible-playbook provisioning/raspbian.yml \
  --inventory=192.168.0.2, \
  --extra-vars "team_number=** team_psk=********"
```
