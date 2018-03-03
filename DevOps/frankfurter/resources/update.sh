#!/bin/bash

# update.sh -- Robot-side script for installing an update
#
# Unpacks a zipped tarball and calls an included script to perform the update.

set -e
updates_dir="$HOME/updates"
mkdir -p "$updates_dir"

for filename in $(find "$updates_dir" -name "*.tar.gz" | sort); do
  echo "Extracting '$updates_dir/$filename' ..."
  tmp_dir="/tmp/$(basename $filename .tar.gz)"
  mkdir -p "$tmp_dir"
  tar -xf "$updates_dir/$filename" -C "$tmp_dir" --warning=no-timestamp

  if [ -e "$tmp_dir/install_update.sh" ]; then
    output=$(cd "$HOME" && bash "$tmp_dir/install_update $tmp_dir" && sync)
    echo "$output"
  else
    echo "Could not find 'install_update' in $filename." >&2
  fi
  rm -rf "$tmp_dir"
  echo "Cleaned up '$tmp_dir'."
done
