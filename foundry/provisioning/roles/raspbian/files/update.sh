#!/bin/bash

# Calls install_update on each of the update tarballs

cd /home/pi
mkdir -p updates && chown pi updates
cd updates

for filename in $(find . -name "*.tar.gz" | sort); do
  proj="$(basename ${filename} ".tar.gz")"
  image=""
  if [ "${proj}" = "runtime" ];
  then
    image="pioneers/runtime:prod"
  fi
  docker stop ${proj}
  docker rm ${proj}
  docker load -i "${filename}"
  docker run --name=${proj} --restart=always --mount source=studentcode,destination=/root/runtime/game/studentcode.py "${image}" 
  rm -f "${filename}"
done
sync
