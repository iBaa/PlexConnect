#!/bin/bash

cd /vagrant/

ip=$(ip addr show eth1 | grep -o 'inet [0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+' | grep -o [0-9].*)
sed "s/##IP##/$ip/" SettingsBase.cfg > Settings.cfg

python PlexConnect.py
