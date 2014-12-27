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
          removecertsbash)
          echo "Output of removecertsbash :<pre>"
          /usr/bin/removecertsbash.bash
          echo "</pre>"
          ;;

          restorecertsbash)
          echo "Output of restorecertsbash :<pre>"
          /usr/bin/restorecertsbash.bash
          echo "</pre>"
          ;;

          createcertbash)
          echo "Output of createcertbash :<pre>"
          /usr/bin/createcertbash.bash
          echo "</pre>"
          ;;

          createimoviebash)
          echo "Output of createimoviebash :<pre>"
          /usr/bin/createimoviebash.bash
          echo "</pre>"
          ;;

          createwsjbash)
          echo "Output of createwsjbash :<pre>"
          /usr/bin/createwsjbash.bash
          echo "</pre>"
          ;;

          createplistbash)
          echo "Output of createplistbash :<pre>"
          /usr/bin/createplistbash.bash
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

          updatewcbash)
          echo "Output of updatewcbash :<pre>"
          /usr/bin/updatewcbash.bash
          echo "</pre>"
          ;;
          
          pmsscanbash)
          echo "Output of pmsscanbash :<pre>"
          /usr/bin/pmsscanbash.bash
          echo "</pre>"
          ;;

          rebootbash)
          echo "Output of rebootbash :<pre>"
          /usr/bin/rebootbash.bash
          echo "</pre>"
          ;;

          lockbash)
          echo "Output of lockbash :<pre>"
          /usr/bin/lockbash.bash
          echo "</pre>"
          ;;
          
          shutdownbash)
          echo "Output of shutdownbash :<pre>"
          /usr/bin/shutdownbash.bash
          echo "</pre>"
          ;;
          
          sleepbash)
          echo "Output of sleepbash :<pre>"
          /usr/bin/sleepbash.bash
          echo "</pre>"
          ;;

          itunesbash)
          echo "Output of itunesbash :<pre>"
          /usr/bin/itunesbash.bash
          echo "</pre>"
          ;;

          quititunesbash)
          echo "Output of quititunesbash :<pre>"
          /usr/bin/quititunesbash.bash
          echo "</pre>"
          ;;

          logbash)
          echo "Output of logbash :<pre>"
          /usr/bin/logbash.bash
          echo "</pre>"
          ;;
          
          whobash)
          echo "Output of whobash :<pre>"
          /usr/bin/whobash.bash
          echo "</pre>"
          ;;
          
          who)
          echo "Output of who :<pre>"
          /usr/bin/who.bash
          echo "</pre>"
          ;;

          wakebash)
          echo "Output of wakebash :<pre>"
          /usr/bin/wakebash.bash
          echo "</pre>"
          ;;

          tvbash)
          echo "Output of tvbash :<pre>"
          /usr/bin/tvbash.bash
          echo "</pre>"
          ;;
          
          trashbash)
          echo "Output of trashbash :<pre>"
          /usr/bin/trashbash.bash
          echo "</pre>"
          ;;

          cyberghostbash)
          echo "Output of cyberghostbash :<pre>"
          /usr/bin/cyberghostbash.bash
          echo "</pre>"
          ;;

          falcobash)
          echo "Output of falcobash :<pre>"
          /usr/bin/falcobash.bash
          echo "</pre>"
          ;;

          ibaabash)
          echo "Output of ibaabash :<pre>"
          /usr/bin/ibaabash.bash
          echo "</pre>"
          ;;

          stoffezbash)
          echo "Output of stoffezbash :<pre>"
          /usr/bin/stoffezbash.bash
          echo "</pre>"
          ;;
          
          backupbash)
          echo "Output of backupbash :<pre>"
          /usr/bin/backupbash.bash
          echo "</pre>"
          ;;
          
          restorebash)
          echo "Output of restorebash :<pre>"
          /usr/bin/restorebash.bash
          echo "</pre>"
          ;;
          
          lognormalbash)
          echo "Output of lognormalbash :<pre>"
          /usr/bin/lognormalbash.bash
          echo "</pre>"
          ;;

          loghighbash)
          echo "Output of loghighbash :<pre>"
          /usr/bin/loghighbash.bash
          echo "</pre>"
          ;;
          
          appwebbash)
          echo "Output of appwebbash :<pre>"
          /usr/bin/appwebbash.bash
          echo "</pre>"
          ;;

	esac
    fi
     
    # print out the form
     
    # page header
    echo "<p>"
    echo "<center>"
    echo "<h2>WebConnect</h2>"
    echo "</center>"
    echo "<p>"
    echo "<p>"
     
    echo "<center>"
    echo "<h2>Please choose your option below</h2>"
    echo "</center>"
    echo "<form method=get>"
    echo "<br>"
    echo "Choose/switch your theme:"
    echo "<br>"
    echo "<input type=radio name=cmd value=ibaabash> Clone iBaa GitHub <br>"
    echo "<input type=radio name=cmd value=cyberghostbash> Clone CyberGhost84 GitHub <br>"
    echo "<input type=radio name=cmd value=falcobash> Clone Falco953 GitHub <br>"
    echo "<input type=radio name=cmd value=stoffezbash> Clone Stoffez GitHub <br>"
    echo "<br>"
    echo "PlexConnect commands:"
    echo "<br>"
    echo "<input type=radio name=cmd value=appwebbash> Update OpenPlex <br>"
    echo "<input type=radio name=cmd value=backupbash> Backup all settings <br>"
    echo "<input type=radio name=cmd value=restorebash> Restore all settings <br>"
    echo "<input type=radio name=cmd value=createplistbash> Install Daemon plist <br>"
    echo "<input type=radio name=cmd value=updaterbash> Update PlexConnect <br>"
    echo "<input type=radio name=cmd value=startbash> Start PlexConnect <br>"
    echo "<input type=radio name=cmd value=stopbash> Stop PlexConnect <br>"
    echo "<input type=radio name=cmd value=restartbash> Restart PlexConnect <br>"
    echo "<input type=radio name=cmd value=lognormalbash> Set loglevel to Normal <br>"
    echo "<input type=radio name=cmd value=loghighbash> Set loglevel to High <br>"
    echo "<input type=radio name=cmd value=statusbash> PlexConnect Status <br>"
    echo "<br>"
    echo "Cert/Hijack management:"
    echo "<br>"
    echo "<input type=radio name=cmd value=restorecertsbash> Restore Certs <br>"
    echo "<input type=radio name=cmd value=removecertsbash> Delete Certs <br>"
    echo "<input type=radio name=cmd value=createcertbash> Generate trailers Certs <br>"
    echo "<input type=radio name=cmd value=createimoviebash> Generate imovie Certs <br>"
    echo "<input type=radio name=cmd value=createwsjbash> Generate wsj Certs <br>"
    echo "<br>"
    echo "<input type=submit>"
    echo "<br>"
    echo "</form>"
    echo "</body>"
    echo "</html>"
