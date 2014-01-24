#!/bin/sh
    echo "Content-type: text/html\n"

    # our html header
    echo "<html>"
    echo "<head><title>OpenConnect</title></head>"
    echo "<body>"

 # read in our parameters
    CMD=`echo "$QUERY_STRING" | sed -n 's/^.*cmd=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"`
    FOLDER=`echo "$QUERY_STRING" | sed -n 's/^.*folder=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`
     FOLDER1=`echo "$QUERY_STRING" | sed -n 's/^.*folder1=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`
FOLDER2=`echo "$QUERY_STRING" | sed -n 's/^.*folder2=\([^&]*\).*$/\1/p' | sed "s/%20/ /g"| sed "s/%2F/\//g"`
     
    # test if any parameters were passed
    if [ $CMD ]
    then
      case "$CMD" in
        createcertbash)
          echo "Output of createcertbash :<pre>"
          /usr/bin/createcertbash.bash
          echo "</pre>"
          ;;

        createplistbash)
          echo "Output of createplistbash :<pre>"
          /usr/bin/createplistbash.bash
          echo "</pre>"
          ;;

        updatebash)
          echo "Output of updatebash :<pre>"
          /usr/bin/updatebash.bash
          echo "</pre>"
          ;;

        startbash)
          echo "Output of startbash :<pre>"
          /usr/bin/startbash.bash
          echo "</pre>"
          ;;

        stopbash)
          echo "Output of stopbash :<pre>"
          /usr/bin/stopbash.bash
          echo "</pre>"
          ;;

        restartbash)
          echo "Output of restartbash :<pre>"
          /usr/bin/restartbash.bash
          echo "</pre>"
          ;;

        createplistnonbash)
          echo "Output of createplistnonbash :<pre>"
          /usr/bin/createplist2.bash
          echo "</pre>"
          ;;

        updatenonbash)
          echo "Output of updatenonbash :<pre>"
          /usr/bin/updatenonbash.bash
          echo "</pre>"
          ;;

	startnonbash)
          echo "Output of startnonbash:<pre>"
          /usr/bin/startnonbash.bash
          echo "</pre>"
          ;; 

         stopnonbash)
          echo "Output of stopnonbash :<pre>"
          /usr/bin/stopnonbash.bash
          echo "</pre>"
          ;;

        restartnonbash)
          echo "Output of restartnonbash :<pre>"
          /usr/bin/restartnonbash.bash
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
    echo "<input type=radio name=cmd value=createcertbash> createcertbash.bash (Install  Certs) <br>"
    echo "</p>"
    echo "Bash Commands"
    echo "<br>"    
    echo "<input type=radio name=cmd value=createplistbash> createplistbash.bash (Install  PlexConnect Bash) <br>"
    echo "<input type=radio name=cmd value=updatebash> updatebash.bash (Update PlexConnect Bash) <br>"
    echo "<input type=radio name=cmd value=startbash> startbash.bash (Start PlexConnect Bash) <br>"
    echo "<input type=radio name=cmd value=stopbash> stopbash.bash (Stop PlexConnect Bash) <br>"
    echo "<input type=radio name=cmd value=restartbash> restartbash.bash (Restart PlexConnect Bash) <br>"
echo "<br>"
    echo "Non-Bash Commands"
    echo "<br>"    
    echo "<input type=radio name=cmd value=createplistnonbash> createplistnonbash.bash (Install  PlexConnect Non-Bash) <br>"
    echo "<input type=radio name=cmd value=updatenonbash> updatenonbash.bash (Update PlexConnect Non-Bash) <br>"
    echo "<input type=radio name=cmd value=startnonbash> startnonbash.bash (Start PlexConnect Non-Bash ) <br>"
    echo "<input type=radio name=cmd value=stopnonbash> stopnonbash.bash (Stop PlexConnect Non-Bash) <br>"
    echo "<input type=radio name=cmd value=restartnonbash> restartnonbash.bash (Restart PlexConnect Non-Bash) <br>"
    echo "<br>"
    echo "<input type=submit>"
    echo "</form>"
    echo "</body>"
    echo "</html>"
