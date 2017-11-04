#!/bin/bash

#make sure to install zip command using sudo apt install.. 
#added zip pkg to master_frankfurter setup

HOST=hostname
ID=192.168.7.1

HOME=ubuntu
USER=192.168.7.2

#format: ssh ubuntu 192.168.7.2 "Linux commands"
#makes a temp directory and goes into the temp directory once made
#gets the logs from the services in the beaglebone and logs in temp directory
#zips log files and prints the zip file name if it has been created
#exit ssh

ssh $HOME@$USER "
mkdir temp
cd temp

journalctl -e -u update.service > update.log
journalctl -e -u runtime.service > service.log
journalctl -e -u networking.service > networking.log
bzip2 * 

cd 

find temp -not -name *bz2 | xargs tar -jcvf archivelogs.tar.bz2 

exit "

#copy and send zip files from remote to local computer
scp $HOME@$USER:archivelogs.tar.bz2 .

#unzip service-logs.zip -d service-logs 
bzip2 -d archivelogs.tar.bz2 
mkdir logs && tar -xf archivelogs.tar -C logs
cd logs && cd temp && bzip2 -d *

