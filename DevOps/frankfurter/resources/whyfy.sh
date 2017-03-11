#!/bin/bash
if [ -f /tmp/whyfi.lock ]; then
echo "checked"; 
else
  touch /tmp/whyfi.lock
  wscan=$(iwlist scan 2>/dev/null | grep -o "\"Team37\"")
  if [ "$wscan" == "" ]; then
    echo "field";
    sudo ifdown ra0;
    sudo ifup ra0=field; 
    else
    echo "student"
  fi

  echo $wscan > /home/ubuntu/res.log
fi
rm /tmp/whyfi.lock
