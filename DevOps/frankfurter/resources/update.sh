#!/bin/bash

# update.sh -- Robot-side script for installing an update
#
# Unpacks a zipped tarball and calls an included script to perform the update.

updates_dir="$HOME/updates"
mkdir -p "$updates_dir"

for filename in $(find "$updates_dir" -name "*.tar.gz" | sort); do
  echo "Extracting '$filename' ..."
  tmp_dir="/tmp/$(basename $filename .tar.gz)"
  mkdir -p "$tmp_dir"
  tar -xf "$filename" -C "$tmp_dir" --warning=no-timestamp --strip-components=1

  if [ -e "$tmp_dir/install_update" ]; then
    output=$(cd "$HOME" && sudo -u ubuntu "$tmp_dir/install_update" "$tmp_dir")
    echo "$output"
  else
    echo "Could not find 'install_update' in $filename." >&2
  fi
  rm "$filename"
  rm -rf "$tmp_dir"
  echo "Cleaned up '$tmp_dir'."
done

sync
