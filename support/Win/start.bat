@echo off

set InstallerPath=%~dp0
set PlexConnectPath=%InstallerPath%..\..\

python %PlexConnectPath%PlexConnect_WinService.py start

echo PlexConnect-Service started
