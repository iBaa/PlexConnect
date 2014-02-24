#!/bin/sh
    echo "Content-type: text/html\n"

    # our html header
    echo "<html>"
    echo "<head><title>OpenConnect</title></head>"
    echo "<body background="http://www.ecardmedia.eu/data/media/907/White_Wallpaper_25.jpg">"
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
          
          statusbash)
          echo "Output of statusbash :<pre>"
          /usr/bin/statusbash.bash
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
          
          updatewcbash)
          echo "Output of updatewcbash :<pre>"
          /usr/bin/updatewcbash.bash
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
    echo "</p>" 
    echo "Cert/Hijack management (Trailers, I-Movie, Wsj, Remove certs)"
    echo "<br>"
    echo "<input type="image" src="http://alliosnews.com/wp-content/uploads/2011/11/Trailers-Icon-150x150.png" name=cmd value=createcertbash>"
    echo "<input type="image" src="http://www5.bluevalleyk12.org/tech-fair/wp-content/uploads/2013/09/iMovie-icon-150x150.jpg" name=cmd value=createimoviebash>"
    echo "<input type="image" src="http://www.csuohio.edu/business/osm/resources/news/images/WSJ-icon.jpg" name=cmd value=createwsjbash>"
echo "<input type="image" src="http://www.icon2s.com/wp-content/uploads/2013/01/Button-Delete-icon-150x150.png" name=cmd value=removecertsbash>"
    echo "</p>"  
    echo "PlexConnect commands (Install, Update, Start, Stop, Status)"
    echo "<br>"
    echo "<input type="image" src="http://static.thetechjournal.net/wp-content/uploads/2011/04/Installous4Icon-iJailbreak-150x150.png" name=cmd value=createplistbash>"
    echo "<input type="image" src="http://www.yourdailymac.net/wp-content/uploads/2011/11/164830-itunes_connect_mobile_icon-150x150.jpg" name=cmd value=updatebash>"
    echo "<input type="image" src="http://seobacklinks4yoursite.com/wp-content/uploads/2013/10/YouTube-icon-150x150.png" name=cmd value=startbash>"
    echo "<input type="image" src="http://www.mybadpad.com/wp-content/uploads/2009/01/stop-sign-150x150.gif" name=cmd value=stopbash>"
    echo "<input type="image" src="http://www.velaction.com/lean-information/wp-content/uploads/2009/09/site-info-icon-150x150.jpg" name=cmd value=statusbash>"
    echo "</p>"
    echo "OSX system commands (Reset, Lock screen)"
    echo "<br>" 
    echo "<input type="image" src="http://www.morningliberty.com/wp-content/uploads/2014/02/reset-150x150.png" name=cmd value=rebootbash>"
    echo "<input type="image" src="http://png-1.findicons.com/files/icons/977/rrze/150/lock.png" name=cmd value=lockbash>"
    echo "<input type="image" src="http://www.baptisttwentyone.com/wp-content/uploads/2011/01/world-globe-icon-150x150.jpg" name=cmd value=updatewcbash>"
    echo "<br>"
    echo "</form>"
    echo "</body>"
    echo "</html>"
