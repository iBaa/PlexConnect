#!/bin/bash

### BEGIN INIT INFO
# Provides:          plexconnect
# Required-Start:    $remote_fs $syslog $networking
# Required-Stop:     
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: PlexConnect
# Description:       PlexConnect
# Author:            PlexConnect Team
# Version:           0.2
### END INIT INFO

# Package
DNAME="PlexConnect"
PNAME="PlexConnect_daemon"

# Others
INSTALL_DIR="."
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


case $1 in
    start)
        if daemon_status; then
            echo ${DNAME} is already running
        else
            echo Starting ${DNAME} ...
            start_daemon
        fi
        ;;
    stop)
        if daemon_status; then
            echo Stopping ${DNAME} ...
            stop_daemon
        else
            echo ${DNAME} is not running
        fi
        ;;
    restart)
        bash $0 stop
        bash $0 start
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
    *)
        exit 1
        ;;
esac