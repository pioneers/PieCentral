#!/bin/sh

CROUTON_URL=https://goo.gl/fd3zc
CROUTON_DIST=trusty
CROUTON_TARGETS=audio,chrome,cli-extra,core,extension,gtk-extra,keyboard,touch,unity-desktop,xiwi,xorg

echo 'Now setting up crouton. At some point, you will be asked to choose a username and password.'
echo 'Please do so when prompted.'

cd ~/Downloads
wget $CROUTON_URL -O crouton
sudo sh crouton -r $CROUTON_DIST -t $CROUTON_TARGETS

rm -f ~/.bashrc
# TODO(vincent): uncomment this once we have the bashrc stuff sorted out
# wget <link to .bashrc file> -O ~/.bashrc

echo 'crouton setup complete! Now logging you into a linux shell.'
echo 'Please run the following script within that shell to complete setup: <Link to script here>'
