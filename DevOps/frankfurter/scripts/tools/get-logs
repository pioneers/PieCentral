#!/bin/bash

HOME=ubuntu
USER=192.168.7.2

#format: ssh ubuntu 192.168.7.2 "Linux commands"
#makes a temp directory and goes into the temp directory once made
#gets the logs from the services in the beaglebone and logs in temp directory
#zips log files and prints the zip file name if it has been created
#exit ssh

ssh $HOME@$USER "
mkdir -p /tmp/log-fetch
cd /tmp/log-fetch

today=$(date +%Y-%m-%d.%H:%M:%S)

journalctl -e -u update.service > update.log"."$today
journalctl -e -u runtime.service > service.log"."$today
journalctl -e -u networking.service > networking.log"."$today

cd 

tar -cjvf archivelogs.tar.bz2 tmp 

exit "

#copy and send zip files from remote to local computer 
#if successful, log back into beaglebone and rm file
scp $HOME@$USER:archivelogs.tar.bz2 . && ssh$HOME@$USER "
rm archivelogs.tar.bz2 
exit "

#unzip service-logs.zip -d service-logs 
bzip2 -d archivelogs.tar.bz2 
tar -xf archivelogs.tar 

