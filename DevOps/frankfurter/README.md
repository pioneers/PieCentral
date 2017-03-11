# frankfurter
Various tools and scripts to make the deployment life easier.

## Before starting...
Note that since all Beaglebone blacks have the same static IP settings by default, after logging
into one (which happens implicitly when you run any of the make targets described below) it is
necessary to remove the corresponding entry in `.ssh/known_hosts` before logging a different Beaglebone
is possible.

## Setting up a Beaglebone Black

There likely won't ever be a way to easily deploy a BBB on Windows. On macOS/Linux, the preferred way of bringing up a Beaglebone is:

1. Get a prebuilt micro SD card from the DevOps box (currently, they are labeled "Frank III").
2. Insert the card into the Beaglebone you wish to flash while the Beaglebone is off.
3. Hold down the `S2` button, and power on the Beaglebone.
4. The Beaglebone will have booted up the image on the card instead of the one in flash memory. `ssh ubuntu@192.168.7.2` in.
5. To commit the image to flash memory, run `sudo /opt/scripts/tools/eMMC/bbb-eMMC-flasher-eewiki-ext4.sh` ([see here](https://github.com/RobertCNelson/boot-scripts/tree/master/tools/eMMC)).
6. Wait about 15 minutes for the image to be flashed.
7. Power down with `sudo shutdown now`.
8. Remove the card.

Alternatively,

1. Download a [stock Ubuntu prebuilt image](http://elinux.org/BeagleBoardUbuntu#eMMC:_All_BeagleBone_Varients_with_eMMC) (preferably 16.04).
2. Follow the instructions given by the link in step 1 to bring up a Beaglebone running stock Ubuntu.
3. Be sure you can `ssh ubuntu@192.168.7.2`. You may need to configure your computer to be able to see the Beaglebone. If you can't `ssh`, run `ifconfig`, identify the name of the interface shared with the Beaglebone, and run `sudo ifconfig <interface> 192.168.7.1`.
4. Connect the Beaglebone to the internet. You should be able to get a response from `ping 8.8.8.8`, but not necessarily from `ping google.com`. One way to do this is to open  `frankfurter/scripts/install/bbb-usb-wifi.sh` in a text editor, carefully modify it to work on your machine, `sudo su`, and run the script. Afterwards, `exit` from `sudo`.
5. On your machine, run `frankfurter/scripts/install/start_frank_install.sh`. Type in `ubuntu`'s password as many times as is necessary.
6. `ssh` in, and run `start_tmux_job.sh`. Again, enter `ubuntu`'s password as necessary.
7. After the kernel is upgraded (to ensure `linux-headers-$(uname -r)` is available), the Beaglebone will automatically reboot. As instructed, reconnect the Beaglebone to the internet after the reboot, `ssh` in, and run `tmux new-session -d '~/PieCentral/DevOps/frankfurter/scripts/install/master_frank_setup.sh'`.
8. Wait about one hour for the Beaglebone to configure and install all dependencies (most of this time is used to build the wireless dongle driver). You can check on the status of your build with `tmux attach`.
9. `sudo reboot`, `ssh` in again, and ensure everything is correctly configured. Try `systemctl status runtime.service`.

### `runtime` and `memcached`

`runtime` is started on boot by `runtime.service` by `systemd` (see pioneers/PieCentral#100, installed to `/lib/systemd/system`).

To interact with the runtime service, run `sudo systemctl <command> runtime.service`, where `<command>` can be:
* `start`
* `restart`
* `stop`
* `status`

`memcached` has been configured to run on port `12357`. See `resources/memcached.conf`.

### Installed Executables

After setup, the following executables are available in `/home/ubuntu/bin`:

| Name         | Purpose                                                                                                            | Notes |
| ------------ | ------------------------------------------------------------------------------------------------------------------ | ----- |
| `mac.py`     | Print the MAC address of a network interface, which is passed as the first argument (see `--help` for details)     | None  |
| `runtime.sh` | Modify `PYTHONPATH` to include the `runtime` and `hibike` directories and execute `runtime`                        | Invoked by `runtime.service` (added to `systemd`) |
| `update.sh`  | Extract all the tarballs in `/home/ubuntu/updates` and installs `hibike` and `runtime` in `/home/ubuntu/PieCentral` | Backs up the last version of `PieCentral` to `PieCentral.backup` |

## Update creation
The `create_update` make target downloads the newest versions of runtime, hibike, etc, and packages them
into a tarball. From here, we can take the files created (they're placed in the
`frankfurter/build` directory) and distribute them to teams, or push them [online](https://pioneers.github.io/dawn/) for Dawn to see.

## Update deployment
`deploy_update` assumes that you're USB tethered to a Beaglebone and then uploads and installs an update
to the connected beaglebone, creating a new update using `create_update` if the `frankfurter/build` directory does not exist.

## Some Notes
1. Beaglebones are set-up using the master branch of PieCentral repository at the time of set-up.
2. When we issue updates we will package both the runtime and hibike directory in a tarball hosted on GitHub pages which will then be extracted into the correct locations on the Beaglebone.
3. Student code is stored in `~/PieCentral/runtime/testy/studentCode.py`.
