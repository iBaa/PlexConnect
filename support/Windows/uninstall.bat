@echo off

set InstallerPath=%~dp0
set PlexConnectPath=%InstallerPath%..\..\

python "%PlexConnectPath%PlexConnect_WinService.py" remove

echo PlexConnect-Service removed
