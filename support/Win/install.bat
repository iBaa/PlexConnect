@echo off

set InstallerPath=%~dp0
set PlexConnectPath=%InstallerPath%..\..\

python %PlexConnectPath%PlexConnect_WinService.py install

echo PlexConnect-Service installed
