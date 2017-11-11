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
cd /temp/log-fetch

journalctl -e -u update.service > update.log
journalctl -e -u runtime.service > service.log
journalctl -e -u networking.service > networking.log 

cd 

tar -cjvf archivelogs.tar.bz2 tmp 

exit "

#copy and send zip files from remote to local computer
scp $HOME@$USER:archivelogs.tar.bz2 .

#unzip service-logs.zip -d service-logs 
bzip2 -d archivelogs.tar.bz2 
tar -xf archivelogs.tar 

