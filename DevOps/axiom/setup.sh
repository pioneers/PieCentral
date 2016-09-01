#!/bin/bash

# super basic setup stuff for axiom assuming that vagrant, virtualbox, and
# virtualbox extensions have been installed. This script will likely be added
# to as we figure out other things that need to be preconfigured for a
# completely clean install.

vagrant box add ubuntu/trusty64 https://atlas.hashicorp.com/ubuntu/boxes/trusty64/versions/20150821.0.0/providers/virtualbox.box
if [ "$(expr substr $(uname -s) 1 5)" == "MINGW" ]; then
  git config --system core.longpaths true
fi
