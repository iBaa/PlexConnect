#!/bin/sh
    echo "Content-type: text/html\n"

    # our html header
    echo "<html>"
    echo "<head><title>WebConnect</title></head>"
    echo "<font color=white><body bgcolor="#A9A9A9">"
    echo "<body>"

 # read in our parameters
    CMD=`echo "$QUERY_STRING" | sed -n 's/^.*cmd=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"`
    FOLDER=`echo "$QUERY_STRING" | sed -n 's/^.*folder=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`
     FOLDER1=`echo "$QUERY_STRING" | sed -n 's/^.*folder1=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`
FOLDER2=`echo "$QUERY_STRING" | sed -n 's/^.*folder2=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`
     
    # print out the form
     
    # page header
    echo "<p>"
    echo "<center>"
    echo "<h2>WebConnect</h2>"
    echo "</center>"
    echo "<p>"
    echo "<p>"
     
    echo "<center>"
    echo "<h2>Please choose your view below</h2>"
    echo "</center>"
    echo "<form method=get>"
    echo "<a href="__OPENPLEX__">OpenPlex View</a>"
    echo "<br>"
    echo "<br>"
    echo "<a href="__LIST__">List View</a>"
    echo "<br>"
    echo "<br>"
    echo "<a href="__INSTALLER__">Installer View</a>"
    echo "<br>"
    echo "<br>"
    echo "<a href="__DEFAULT__">Default View</a>"
    echo "<br>"
    echo "<br>"
    echo "<a href="__IOS__">IOS View</a>"
    echo "<br>"
    echo "<br>"
    echo "<br>"
    echo "</form>"
    echo "</body>"
    echo "</html>"
