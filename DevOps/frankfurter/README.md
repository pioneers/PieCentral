# frankfurter
Various tools and scripts to make the deployment life easier.

## Before starting...
Note that since all Beaglebone blacks have the same static IP settings by default, after logging
into one (which happens implicitly when you run any of the make targets described below) it is
necessary to remove the corresponding entry in `.ssh/known_hosts` before logging a different Beaglebone
is possible.

## Setting up a Beaglebone Black
Assuming you're running Linux/OSX, only three things need to be done. There likely won't ever be a
way to easily deploy a BBB on Windows.

1. Flash the Beaglebone's eMMC as outlined [here](http://elinux.org/Beagleboard:Ubuntu_On_BeagleBone_Black#Main_Process)
(Follow Sections 1 and 4). We have quite a few SD cards with the image already flashed on them in the DevOps box.
2. Inside the frankfurter directory, run `make beaglebone_install`.
3. You'll be asked to enter the default password of the BBB twice, and afterwards you'll be logged into
   the BBB. From here, run `./start_tmux_job.sh`, and enter the default password one more time to initiate
   setup. The script will do some stuff and eventually print 'Disconnect OK' to the console. At this point,
   feel free to (assuming you keep the Beaglebone powered in some way) exit your ssh session with the
   Beaglebone. When everything is finished, the file ~/DONE will be created.
   (TODO: this step less clunky if possible)

## Update creation
The `create_update` make target downloads the newest versions of runtime, hibike, etc, packages them
into a tarball, and signs the tarball. From here, we can take the files created (they're placed in the
build/ directory) and distribute them to teams.

## Update deployment
`deploy_update` assumes that you're USB tethered to a Beaglebone and then uploads and installs an update
to the connected beaglebone, creating a new update using `create_update` if the build/ directory does not
exit.
