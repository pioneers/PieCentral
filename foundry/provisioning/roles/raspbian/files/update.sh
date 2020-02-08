#!/bin/bash

# Calls install_update on each of the update tarballs

cd /home/ubuntu
mkdir -p updates && chown ubuntu:ubuntu updates
cd updates

for filename in $(find . -name "*.tar.gz" | sort); do
  tmp="/tmp/$(basename ${filename} .tar.gz)"

  docker load -i "${filename}"
  image="$(basename ${filename} ".tar.gz")"
  docker stop "${image}"
  docker rm "${image}"
  docker run "${image}" --restart=always
  rm "${filename}"
  rm -rf "${tmp}"
done
sync
