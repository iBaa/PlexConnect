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
     
    # test if any parameters were passed
    if [ $CMD ]
    then
      case "$CMD" in
        updatewcbash)
          echo "Output of updatewcbash :<pre>"
          /usr/bin/updatewcbash.bash
          echo "</pre>"
          ;;

          updaterbash)
          echo "Output of updaterbash :<pre>"
          /usr/bin/updaterbash.bash
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
          
          statusbash)
          echo "Output of statusbash :<pre>"
          /usr/bin/statusbash.bash
          echo "</pre>"
          ;;

	esac
    fi
     
    # print out the form
     
    # page header
echo "<form method=get>"
    echo "</p>"
    echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://raw.githubusercontent.com/wahlmanj/OpenPlex/master/OpenPlexIcons/status.png" name=cmd title=Status_PlexConnect value=statusbash>"
    echo "<br>"
echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://raw.githubusercontent.com/wahlmanj/OpenPlex/master/OpenPlexIcons/OP-Logo.png" name=cmd title= Update_WebConnect value=updatewcbash>"
echo "<br>"
    echo "<input type="image" img src="https://raw.githubusercontent.com/wahlmanj/OpenPlex/master/OpenPlexIcons/startplex.png" name=cmd title=Start_PlexConnect value=startbash>&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://raw.githubusercontent.com/wahlmanj/OpenPlex/master/OpenPlexIcons/stopplex.png" name=cmd title= Stop_PlexConnect value=stopbash>&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" img src="https://raw.githubusercontent.com/wahlmanj/OpenPlex/master/OpenPlexIcons/update.png" name=cmd title= Update_PlexConnect value=updaterbash>"
    echo "<br>"
    echo "</form>"
    echo "</body>"
    echo "</html>"
