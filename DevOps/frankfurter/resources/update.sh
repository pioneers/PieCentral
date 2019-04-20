#!/bin/bash

cd /home/ubuntu
mkdir -p updates && chown ubuntu:ubuntu updates
cd updates

for filename in $(find . -name "*.tar.gz" | sort); do
  tmp="/tmp/$(basename ${filename} .tar.gz)"
  mkdir -p "${tmp}"
  tar -xf "${filename}" -C "${tmp}" --strip-components=1
  if [ -e "${tmp}/install_update" ]; then
    bash "${tmp}/install_update" "${tmp}"
  fi
  rm "${filename}"
  rm -rf "${tmp}"
done
sync
