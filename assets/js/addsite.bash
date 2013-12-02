#!/bin/bash

## replace the __REPLACE_THIS_PATH__ variables with your web server local/remote ip or dyndns 

sed -i '' 's/http:\/\/atv.plexconnect/http:\/\/__REPLACE_THIS_PATH__/g' *js
