# frankfurter
Various tools and scripts to make the deployment life easier.

## Setting up a "master copy" of frank
Ideally, only three things need to be done.

1. Flash the Beaglebone's eMMC as outlined in
http://elinux.org/Beagleboard:Ubuntu_On_BeagleBone_Black#Main_Process (Follow Sections 1 and 4).
2. Set up internet sharing from your PC to the Beaglebone Black. Instructions for this can be found
at https://elementztechblog.wordpress.com/2014/12/22/sharing-internet-using-network-over-usb-in-beaglebone-black/
Be sure to change the network devices being used in the examples appropriately.
3. Install git (may require you to update apt-get), clone this repo, and run
scripts/master_frank_setup.sh (TODO: integrate Chris' network setup stuff)

That's it! From here we'll be pulling the image from our frank master copy to further flash to the
rest of the Beaglebone Blacks.

## Setting up clones of frank
Setting up a clone of frank (for a team) only involves doing 2 things.

1. Flash the Beaglebone's eMMC with the master frank image (we'll get this on the wiki once it's made)
2. Wait until it finishes.

## Update deployment
Deploying an update is simple. All you have to do is run scripts/deploy_update.sh. This will output
two files: the tarball itself and a signature (the .asc file).

Currently, deploying an update does a few things.

1. The latest versions of hibike and runtime are downloaded to be included in the tarball.
2. scripts/install_update.sh is also copied to be packaged. This file contains the instructions for
installing this particular update, so any additional packages to install, etc. that come up in the
future should be added to that script. Of course, keep in mind that the script should be written
such that the update can be applied regardless of the state of the robot given that the base frank
image has been flashed to it.
3. Everything is packed into a tarball which is then signed using gpg. Ask Vincent for the private
key needed to sign tarballs.
