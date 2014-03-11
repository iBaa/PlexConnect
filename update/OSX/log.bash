#!/bin/bash

echo 'This command displays your plexconnect log file continuously'
echo 'You must navigate to the previous page for your icons or list to reappear'

## Display PlexConnect log
tail -f /applications/plexconnect/plexconnect.log
