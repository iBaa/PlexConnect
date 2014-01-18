display dialog "Welcome to OpenConnect" giving up after 2
set question to display dialog "What option would you like?" buttons {"Guide", "Expert"} default button 2
set answer to button returned of question

if answer is equal to "Expert" then
	set question to display dialog "Pick your option below" buttons {"Install Cert", "Install PlexConnect", "Update PlexConnect"} default button 2
	set answer to button returned of question
end if

if answer is equal to "Install PlexConnect" then
	set question to display dialog "Which plist bash or non-bash?" buttons {"bash", "non-bash"} default button 2
	set answer to button returned of question
end if

if answer is equal to "Update PlexConnect" then
	set question to display dialog "Which plist bash or non-bash?" buttons {"update bash", "update non-bash"} default button 2
	set answer to button returned of question
end if

if answer is equal to "Guide" then
	set question to display dialog "Have you installed your certs yet?" buttons {"Yes", "Install Certs"} default button 2
	set answer to button returned of question
end if

if answer is equal to "Yes" then
	set question to display dialog "Install PlexConnect?" buttons {"Ok", "Nah"} default button 2
	set answer to button returned of question
end if

if answer is equal to "Install Cert" then
	do shell script "createcert.bash" with administrator privileges
	display dialog "Creating Cert..." giving up after 2
	set question to display dialog "Certs have been generated" giving up after 2
	display dialog "Goodbye!" giving up after 3
end if

if answer is equal to "Install Certs" then
	do shell script "createcert.bash" with administrator privileges
	display dialog "Creating Cert..." giving up after 2
	set question to display dialog "Certs have been generated. Copy your new cert to your apple tv (they are located at assets/certificates)" buttons {"Guide Me", "Skip"} default button 2
	set answer to button returned of question
	if answer is equal to "Guide Me" then
		set theURL to "https://github.com/iBaa/PlexConnect/wiki/Install-Guide-Certificate-via-USB"
		tell application "Safari" to make new document with properties {URL:theURL}
	end if
end if

if answer is equal to "Skip" then
	set question to display dialog "Install PlexConnect?" buttons {"Ok", "Nah"} default button 2
	set answer to button returned of question
end if

if answer is equal to "Ok" then
	set question to display dialog "Which plist bash or non-bash?" buttons {"bash", "non-bash"} default button 2
	set answer to button returned of question
end if

if answer is equal to "bash" then
	try
		do shell script "createplist.bash" with administrator privileges
		display dialog "Installing PlexConnect..." giving up after 1
		display dialog "Starting PlexConnect..." giving up after 1
		do shell script "update.bash" with administrator privileges
		display dialog "Updating PlexConnect..." giving up after 2
		display dialog "PlexConnect has been updated..." giving up after 2
		display dialog "Goodbye!" giving up after 3
	end try
end if

if answer is equal to "non-bash" then
	try
		do shell script "createplist2.bash" with administrator privileges
		display dialog "Installing PlexConnect..." giving up after 1
		display dialog "Starting PlexConnect..." giving up after 1
		do shell script "update2.bash" with administrator privileges
		display dialog "Updating PlexConnect..." giving up after 2
		display dialog "PlexConnect has been updated..." giving up after 2
		display dialog "Goodbye!" giving up after 3
	end try
end if

if answer is equal to "Nah" then
	set question to display dialog "Would you like to Update?" buttons {"Please", "Nope"} default button 2
	set answer to button returned of question
end if

if answer is equal to "Please" then
	set question to display dialog "Which plist bash or non-bash?" buttons {"update bash", "update non-bash"} default button 2
	set answer to button returned of question
end if

if answer is equal to "update bash" then
	try
		do shell script "update.bash" with administrator privileges
		display dialog "Updating PlexConnect..." giving up after 2
		display dialog "PlexConnect has been updated..." giving up after 2
		display dialog "Goodbye!" giving up after 3
	end try
end if

if answer is equal to "update non-bash" then
	try
		do shell script "update2.bash" with administrator privileges
		display dialog "Updating PlexConnect..." giving up after 2
		display dialog "PlexConnect has been updated..." giving up after 2
		display dialog "Goodbye!" giving up after 3
	end try
end if

if answer is equal to "Nope" then
	display dialog "Goodbye!" giving up after 3
end if
