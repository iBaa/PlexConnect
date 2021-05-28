#!/bin/bash

#
# Linux PlexConnect start stop script
#

# Package
DNAME="PlexConnect"
PNAME="PlexConnect_daemon"

# Others
export PYTHONHTTPSVERIFY=0
# current path resolver from http://stackoverflow.com/a/246128
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
INSTALL_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

PYTHON="python"
PROGRAM="${INSTALL_DIR}/${PNAME}.py"
PID_FILE="/var/${PNAME}.pid"


start_daemon ()
{
    cd "${INSTALL_DIR}"
    ${PYTHON} ${PROGRAM} --pidfile ${PID_FILE}
}

stop_daemon ()
{
    kill `cat ${PID_FILE}`
    wait_for_status 1 20 || kill -9 `cat ${PID_FILE}`
    rm -f ${PID_FILE}
}

daemon_status ()
{
    if [ -f ${PID_FILE} ] && kill -0 `cat ${PID_FILE}` > /dev/null 2>&1; then
        return
    fi
    rm -f ${PID_FILE}
    return 1
}

wait_for_status ()
{
    counter=$2
    while [ ${counter} -gt 0 ]; do
        daemon_status
        [ $? -eq $1 ] && return
        let counter=counter-1
        sleep 1
    done
    return 1
}

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

# Determine if the operating system is OSX "darwin". If so, then delay running the rest of
# the script until the network is up. This avoids the binding of PlexConnect to the
# loopback address which occurs if the bash script is called from a LaunchDaemon/plist
# file at boot time. 

if [[ "$OSTYPE" == "darwin"* ]]; then
CheckForNetwork
	while [ "${NETWORKUP}" != "-YES-" ]
	do
		sleep 5
		NETWORKUP=
		CheckForNetwork
	done
fi

# Now do what you need to do.

case $1 in
    start)
        if daemon_status; then
            echo ${DNAME} is already running
        else
            echo Starting ${DNAME}...
            start_daemon
        fi
        ;;
    stop)
        if daemon_status; then
            echo Stopping ${DNAME}...
            stop_daemon
        else
            echo ${DNAME} is not running
        fi
        ;;
    status)
        if daemon_status; then
            echo ${DNAME} is running
            exit 0
        else
            echo ${DNAME} is not running
            exit 1
        fi
        ;;
    restart)
        $0 stop && sleep 2 && $0 start && sleep 2 && $0 status
        ;;
    *)
        exit 1
        ;;
esac
