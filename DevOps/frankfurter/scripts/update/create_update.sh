#!/bin/bash

##############################################################################################
# Pulls the newest versions of hibike and  runtime from github and packages them nicely      #
# in a tarball along with the install_update.sh script. Then proceeds to digitally sign      #
# the file so that the signature can be verified before the robot uses the tarball to update #
##############################################################################################

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/DevOps/frankfurter
BUILD_DIR=$FRANKFURTER_DIR/build
TMP_DIR=$BUILD_DIR/build

if [ -d "$BUILD_DIR" ]; then
  echo "Removing old build directory ... "
  rm -rf $BUILD_DIR
fi

echo "Making new build directory ... "
mkdir -p $BUILD_DIR
mkdir -p $TMP_DIR
echo "Done."

git pull
cp -R $(git rev-parse --show-toplevel)/hibike $TMP_DIR/hibike
cp $FRANKFURTER_DIR/scripts/update/install_update.sh $TMP_DIR

CURRENT_TIME=$(date +%s%N)
UPDATE_FILENAME=frankfurter-update-"$CURRENT_TIME".tar.gz

cd $BUILD_DIR
tar -zcf $UPDATE_FILENAME --directory=$TMP_DIR .
echo "==> Tarball available at: "
echo $BUILD_DIR/$UPDATE_FILENAME

rm -rf $TMP_DIR
echo "Cleaned up."
