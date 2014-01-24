#!/bin/sh
    echo "Content-type: text/html\n"
     
    # read in our parameters
    CMD=`echo "$QUERY_STRING" | sed -n 's/^.*cmd=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"`
    FOLDER=`echo "$QUERY_STRING" | sed -n 's/^.*folder=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`
     FOLDER1=`echo "$QUERY_STRING" | sed -n 's/^.*folder1=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`
FOLDER2=`echo "$QUERY_STRING" | sed -n 's/^.*folder2=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`

    # our html header
    echo "<html>"
    echo "<head><title>OpenConnect</title></head>"
    echo "<body>"
     
    # test if any parameters were passed
    if [ $CMD ]
    then
      case "$CMD" in
        createcert)
          echo "Output of createcert :<pre>"
          /usr/bin/createcert.bash
          echo "</pre>"
          ;;

        createplist)
          echo "Output of createplist :<pre>"
          /usr/bin/createplist.bash
          echo "</pre>"
          ;;

        update)
          echo "Output of update :<pre>"
          /usr/bin/update.bash
          echo "</pre>"
          ;;

        start)
          echo "Output of start :<pre>"
          /usr/bin/start.bash
          echo "</pre>"
          ;;

        stop)
          echo "Output of stop :<pre>"
          /usr/bin/stop.bash
          echo "</pre>"
          ;;

        restart)
          echo "Output of restart :<pre>"
          /usr/bin/restart.bash
          echo "</pre>"
          ;;

        createplist2)
          echo "Output of createplist2 :<pre>"
          /usr/bin/createplist2.bash
          echo "</pre>"
          ;;

        update2)
          echo "Output of update2 :<pre>"
          /usr/bin/update2.bash
          echo "</pre>"
          ;;

	start2)
          echo "Output of start2:<pre>"
          /usr/bin/start2.bash
          echo "</pre>"
          ;; 

         stop2)
          echo "Output of stop2 :<pre>"
          /usr/bin/stop2.bash
          echo "</pre>"
          ;;

        restart2)
          echo "Output of restart2 :<pre>"
          /usr/bin/restart2.bash
          echo "</pre>"
          ;;

	esac
    fi
     
    # print out the form
     
    # page header
    echo "<p>"
    echo "<center>"
    echo "<h2>OpenConnect</h2>"
    echo "</center>"
    echo "<p>"
    echo "<p>"
     
    echo "<center>"
    echo "<h2>Please choose your option below</h2>"
    echo "</center>"
    echo "<form method=get>"
    echo "<br>"
    echo "Create Certs"
    echo "<br>"
    echo "<input type=radio name=cmd value=createcert> createcert.bash (Install  Certs) <br>"
    echo "</p>"
    echo "Bash Commands"
    echo "<br>"    
    echo "<input type=radio name=cmd value=createplist> createplist.bash (Install  PlexConnect Bash) <br>"
    echo "<input type=radio name=cmd value=update> update.bash (Update PlexConnect Bash) <br>"
    echo "<input type=radio name=cmd value=start> start.bash (Start PlexConnect Bash) <br>"
    echo "<input type=radio name=cmd value=stop> stop.bash (Stop PlexConnect Bash) <br>"
    echo "<input type=radio name=cmd value=restart> restart.bash (Restart PlexConnect Bash) <br>"
echo "<br>"
    echo "Non-Bash Commands"
    echo "<br>"    
    echo "<input type=radio name=cmd value=createplist2> createplist2.bash (Install  PlexConnect Non-Bash) <br>"
    echo "<input type=radio name=cmd value=update2> update2.bash (Update PlexConnect Non-Bash) <br>"
    echo "<input type=radio name=cmd value=start2> start2.bash (Start PlexConnect Non-Bash ) <br>"
    echo "<input type=radio name=cmd value=stop2> stop2.bash (Stop PlexConnect Non-Bash) <br>"
    echo "<input type=radio name=cmd value=restart2> restart2.bash (Restart PlexConnect Non-Bash) <br>"
    echo "<br>"
    echo "<input type=submit>"
    echo "</form>"
    echo "</body>"
    echo "</html>"
