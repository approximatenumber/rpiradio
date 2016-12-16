#!/bin/bash

cd /home/pi/rpiradio
source rpiradio_conf.py

cur_max_st=`wc -l $PLAYLIST_PATH/$PLAYLIST| awk '{print $1}'`
sed -i "s/MAX_STATIONS=*[0-9]*/MAX_STATIONS=${cur_max_st}/g" rpiradio_conf.py
/etc/init.d/mpd restart
mpc clear
mpc load $PLAYLIST
python rpiradio.py &
while true; do
    sleep 3
    if [ -f /tmp/radio.reset ]
    then
	rm /tmp/radio.reset
	/etc/init.d/mpd stop
	pkill -f mpd
	pkill -f python
	sleep 12			# without timeout 5..15 sec mpc can`t start properly, I don`t know why...
	/etc/init.d/mpd restart
	mpc clear
	mpc load $PLAYLIST
	sleep 1
	python rpiradio.py &
    else
	echo ok > /dev/null
    fi
done 
