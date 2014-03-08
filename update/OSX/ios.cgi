#!/bin/sh
    echo "Content-type: text/html\n"

    # our html header
    echo "<html>"
    echo "<head><title>WebConnect</title></head>"
    echo "<font color=white><body bgcolor="black">"
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
          
          pmsscanbash)
          echo "Output of pmsscanbash :<pre>"
          /usr/bin/pmsscanbash.bash
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

	esac
    fi
     
    # print out the form
     
    # page header
    echo "<form method=get>"
    echo "<br>"
    echo "</p>" 
    echo "<br>"
    echo "<input type="image" src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-57392100-1393300878.png" name=cmd value=createcertbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" img src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-86675500-1393300317.png" name=cmd value=createimoviebash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-49702700-1393301045.png" name=cmd value=createwsjbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-72591000-1393300768.png" name=cmd value=removecertsbash>"
    echo "<br>"
    echo "<br>"
    echo "<br>"
    echo "<input type="image" src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-09149600-1393299823.png" name=cmd value=createplistbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" img src="https://forums.plex.tv/uploads/monthly_03_2014/post-137692-0-32431000-1394050470.png" name=cmd value=updatebash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" img src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-55882700-1393308785.png" name=cmd value=startbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-33949100-1393308823.png" name=cmd value=stopbash>"
    echo "<br>"
    echo "<br>"
    echo "<br>"
    echo "<input type="image" src="http://f.cl.ly/items/363I1j260v1r2h1F192y/AppIcon.png" name=cmd value=pmsscanbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="__PLEXWEB__"><img src="http://i.imgur.com/Qbw5v.png" alt="P"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://forums.plex.tv/uploads/monthly_03_2014/post-137692-0-51836900-1394049969.png" name=cmd value=updatewcbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-87751600-1393308909.png" name=cmd value=statusbash>"
    echo "<br>"
    echo "<br>"
    echo "<br>"
    echo "<input type="image" src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-77136700-1393308060.png" name=cmd value=rebootbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" img src="https://forums.plex.tv/uploads/monthly_02_2014/post-137692-0-02833300-1393300878.png" name=cmd value=lockbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://forums.plex.tv/uploads/monthly_03_2014/post-137692-0-10866700-1394138870.png" name=cmd value=sleepbash>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="https://forums.plex.tv/uploads/monthly_03_2014/post-137692-0-20697100-1394139146.png" name=cmd value=shutdownbash>"
    echo "<br>"
    echo "<br>"
    echo "<br>"
    echo "<a href="__PLEXWEBWAN__"><img src="http://i.imgur.com/Qbw5v.png" alt="P"></a>"
    echo "<br>"
    echo "<br>"
    echo "<br>"
    echo "<a href="http://alturl.com/5js9g"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" alt="PayPal - The safer, easier way to pay online!"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="http://alturl.com/j8xdb"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" alt="PayPal - The safer, easier way to pay online!"></a>"
    echo "<br>"
    echo "</form>"
    echo "</body>"
    echo "</html>"
