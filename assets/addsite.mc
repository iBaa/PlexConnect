<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadDescription</key>
    <string>Enable Add Site</string>
    <key>PayloadDisplayName</key>
    <string>Enable Add Site</string>
    <key>PayloadIdentifier</key>
    <string>com.apple.frontrow.add_site</string>
    <key>PayloadOrganization</key>
    <string>Apple, Inc</string>
    <key>PayloadRebootSuggested</key>
    <false/>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>3DEFA8CE-1966-4D85-A508-D8852199439A</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>PayloadIdentifier</key>
            <string>com.apple.defaults.1</string>
            <key>PayloadType</key>
            <string>com.apple.defaults.managed</string>
            <key>PayloadUUID</key>
            <string>E5FFD95D-9A16-45BE-B47A-E05FB3E275CF</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>PayloadContent</key>
            <array>
                <dict>
                    <key>DefaultsDomainName</key>
                    <string>com.apple.frontrow</string>
                    <key>DefaultsData</key>
                    <dict>
                        <key>F2BE6C81-66C8-4763-BDC6-385D39088028</key>
                        <dict>
                            <key>EnableAddSite</key>
                            <true/>
                            <!-- Update the logging URL below to point to your HTTP logging destination URL. See the sample site for details. -->
                            <key>AddSiteLoggingURL</key>
                            <string>http://__IP_ADDR__/log</string>
                        </dict>
                    </dict>
                </dict>
            </array>
        </dict>
    </array>
</dict>
</plist>
