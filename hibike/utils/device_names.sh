#/bin/bash

#returns a list of all device names.  Used in combination with other linux hackery for tab-completion


#this function is not meant to be called from the "utils" folder.  It will fail because of pathing problems.
#it is meant to be called from the "hibike" folder, since that is where flash.sh is located.
set -e
cd devices/
echo *
