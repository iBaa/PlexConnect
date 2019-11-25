#!/bin/bash

#
# OSX PlexConnect startup script
#

# Package
APPNAME="PlexConnect.py"


# Determine if the network is up by looking for any non-loopback network interfaces.
# Currently supports only OSX "Darwin" OS
CheckForNetwork()
{
    local test
    
    if [ -z "${NETWORKUP:=}" ]; then
        test=$(ifconfig -a inet 2>/dev/null | sed -n -e '/127.0.0.1/d' -e '/0.0.0.0/d' -e '/inet/p' | wc -l)
        if [ "${test}" -gt 0 ]; then
            NETWORKUP="-YES-"
        else
            NETWORKUP="-NO-"
        fi
    fi
}


# Wait for network readiness.
# This avoids the binding of PlexConnect to the loopback address which may otherwise occur
# if the bash script is called from a LaunchDaemon/plist file at boot time.

CheckForNetwork
while [ "${NETWORKUP}" != "-YES-" ]
do
    sleep 5
    NETWORKUP=
    CheckForNetwork
done


# Start PlexConnect
./${APPNAME}
