#!/bin/sh

BASHRC_URL=https://raw.githubusercontent.com/pioneers/PieCentral/master/DevOps/chrommunal/bashrc
CROUTON_URL=https://goo.gl/fd3zc
CROUTON_DIST=trusty
CROUTON_TARGETS=audio,chrome,cli-extra,core,extension,gtk-extra,keyboard,touch,unity-desktop,xiwi,xorg

echo 'Now setting up crouton. At some point, you will be asked to choose a username and password.'
echo 'Please do so when prompted.'

cd ~/Downloads
wget $CROUTON_URL -O crouton
sudo sh crouton -r $CROUTON_DIST -t $CROUTON_TARGETS

rm -f ~/.bashrc
wget $BASHRC_URL -O ~/.bashrc

echo 'crouton setup complete! Now logging you into a linux shell.'
echo 'Please run the following script within that shell to complete setup:'
echo 'wget -O - https://raw.githubusercontent.com/pioneers/PieCentral/master/DevOps/chrommunal/setup-ubuntu.sh | bash'
sudo wget -P /usr/local/bin/ https://raw.githubusercontent.com/KittyKatt/screenFetch/master/screenfetch-dev
sudo chmod +x /usr/local/bin/screenfetch-dev
sudo enter-chroot
