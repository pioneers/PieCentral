#!/bin/bash

# Reloads docker images placed in /home/pi/updates
# Calls install_update on update tarballs

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

  if [ "${proj}" =~ "update" ]
  then
    tmp="/tmp/$(basename ${filename} .tar.gz)"
    mkdir -p "${tmp}"
    tar -xf "${filename}" -C "${tmp}" --strip-components=1
    if [ -e "${tmp}/install_update" ]; then
      bash "${tmp}/install_update" "${tmp}"
    fi
    rm "${filename}"
    rm -rf "${tmp}"
  else
    docker stop ${proj}
    docker load -i "${filename}"
    systemctl restart ${proj}.service
    rm -f "${filename}"
  fi
done
sync
