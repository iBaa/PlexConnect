#!/bin/bash

## cd to PlexConnect directory
cd __INSTALLERPATH__
cd ../..
PlexConnectPath=${PWD}


sed -i '' 's/trailers.apple.com/www.icloud.com/g' settings.cfg
sed -i '' 's/secure.marketwatch.com/www.icloud.com/g' settings.cfg

## check SSL certificate
file="${PlexConnectPath}/assets/certificates/trailers.pem"
if [ -f "$file" ]; then
    echo 'SSL certificate '$file' found. Skipping' 
    echo 'Settings.cfg changed to hijack www.icloud.com'
    echo 'Upload profile to ATV using this url http://www.icloud.com/trailers.cer'
else

## Trailers - hostname is trailers.apple.com
## certificate good for 10 years
openssl req -new -nodes -newkey rsa:2048 -out ./assets/certificates/trailers.pem -keyout ./assets/certificates/trailers.key -x509 -days 3650 -subj "/C=US/CN=www.icloud.com"
openssl x509 -in ./assets/certificates/trailers.pem -outform der -out ./assets/certificates/trailers.cer && cat ./assets/certificates/trailers.key >> ./assets/certificates/trailers.pem

sed -i '' 's/trailers.apple.com/www.icloud.com/g' settings.cfg
sed -i '' 's/secure.marketwatch.com/www.icloud.com/g' settings.cfg

echo 'Generating Imovie certs'
echo 'Settings.cfg changed to hijack www.icloud.com'
echo 'Upload profile to ATV using this url http://www.icloud.com/trailers.cer'
restart.bash
