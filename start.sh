#!/bin/bash

cd /home/pi/piradio

cp "stations.m3u" "/var/lib/mpd/playlists"

python checker.py

if test $? -ne 0; then
    python radio.py &> radio.log
fi
