#!/bin/bash

## cd to PlexConnect directory
cd __INSTALLERPATH__
cd ../..
PlexConnectPath=${PWD}

sed -i '' 's/trailers.apple.com/secure.marketwatch.com/g' settings.cfg
sed -i '' 's/www.icloud.com/secure.marketwatch.com/g' settings.cfg

## check SSL certificate
file="${PlexConnectPath}/assets/certificates/wsj.pem"
if [ -f "$file" ]; then
    echo 'SSL certificate '$file' found. Skipping' 
    echo 'Settings.cfg changed to hijack secure.marketwatch.com'
    echo 'Upload profile to ATV using this url http://secure.marketwatch.com/wsj.cer'
else

## Trailers - hostname is secure.marketwatch.com
## certificate good for 10 years
openssl req -new -nodes -newkey rsa:2048 -out ./assets/certificates/trailers.pem -keyout ./assets/certificates/trailers.key -x509 -days 3650 -subj "/C=US/CN=trailers.apple.com"
openssl x509 -in ./assets/certificates/trailers.pem -outform der -out ./assets/certificates/trailers.cer && cat ./assets/certificates/trailers.key >> ./assets/certificates/trailers.pem

openssl req -new -nodes -newkey rsa:2048 -out ./assets/certificates/imovie.pem -keyout ./assets/certificates/imovie.key -x509 -days 3650 -subj "/C=US/CN=www.icloud.com"
openssl x509 -in ./assets/certificates/imovie.pem -outform der -out ./assets/certificates/imovie.cer && cat ./assets/certificates/imovie.key >> ./assets/certificates/imovie.pem

openssl req -new -nodes -newkey rsa:2048 -out ./assets/certificates/wsj.pem -keyout ./assets/certificates/wsj.key -x509 -days 3650 -subj "/C=US/CN=secure.marketwatch.com"
openssl x509 -in ./assets/certificates/wsj.pem -outform der -out ./assets/certificates/wsj.cer && cat ./assets/certificates/wsj.key >> ./assets/certificates/wsj.pem

sed -i '' 's/trailers.apple.com/secure.marketwatch.com/g' settings.cfg
sed -i '' 's/www.icloud.com/secure.marketwatch.com/g' settings.cfg

echo 'Generating WSJ certs'
echo 'Settings.cfg changed to hijack secure.marketwatch.com'
echo 'Upload profile to ATV using this url http://secure.marketwatch.com/wsj.cer'
restart.bash

fi
