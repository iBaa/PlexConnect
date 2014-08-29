curl -H "User-Agent: iTunes-AppleTV/6.2 (2; 8GB; dt:11)" https://itunes.apple.com/WebObjects/MZStore.woa/wa/storeFront | sed 's/&lt;/</g; s/&gt;/>/g' > /Applications/PlexConnect/update/OSX/storeFront
