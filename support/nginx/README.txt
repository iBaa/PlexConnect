You can use these sample .conf files to create reverse proxy rules.

These files contain some parameters that you need to edit:

	1. %pc_host_name% - usually trailers.apple.com unless you opted to intercept another app
	2. %cert_name% - usually trailers unless you have generated certs with another name
	3. %ip_plexconnect% - The IP of the device where you have PlexConnect installed
	4. %port_webserver% - Must be equal to port_webserver in Settings.cfg (suggested value 81)
	5. %port_ssl% - Must be equal to port_ssl in Settings.cfg (suggested value 444)

To install pls refer to your operating system instructions. In some cases it's as simple as
copying to the folder that already contains nginx.conf and restart nginx
