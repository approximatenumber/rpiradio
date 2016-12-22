#!/usr/bin/python2

import time
from nanpy import Arduino, Lcd
from mpd import MPDClient


def say_hello():
    """
    Just prints hello on startup
    """
    lcd.printString(16*" ", 0, 0)
    lcd.printString(16*" ", 0, 1)
    lcd.printString("     piradio     ", 0, 0)
    lcd.printString("Starting play...", 0, 1)
    time.sleep(2)


def init_playlist():
    """
    Recreates playlist from config
    """
    mpc.clear()
    mpc.load('stations')


def detect_button():
    """
    Detects the value of the pressed button and returns the appropriate key
    """
    button_values =  {"NEXT"  : range(0, 50),
                      "VUP"   : range(51, 250),
                      "VDOWN" : range(251, 300),
                      "PREV"  : range(301, 500),
                      "PLAY"  : range(501, 700)
                     }

    val = Arduino.analogRead(14)
    for key in button_values:
        if val in button_values[key]:
            return key


def show_info():
    """
    Prints messages on LCD
    """
    mpc_state = mpc.status()['state']
    vol_value = mpc.status()['volume']
    current_song = mpc.currentsong()['file']
    current_song_id = int(mpc.status()['song'])+1

    playlistlength = mpc.status()['playlistlength']

    lcd.printString(16*" ", 0, 0)
    lcd.printString(mpc_state.upper(), 0, 0)
    lcd.printString("VOL%s%%" % vol_value, 6, 0)
    lcd.printString("%s/%s" % (current_song_id, playlistlength), 13, 0)

    lcd.printString(16*" ", 0, 1)
    lcd.printString(current_song[0:15], 0, 1)
    time.sleep(1.5)
    lcd.printString(current_song[16:], 0, 1)


def pause():
    mpc.pause()
    show_info()

def play():
    mpc.play()
    show_info()

def next():
    mpc.next()
    mpc.play()
    show_info()

def previous():
    mpc.previous()
    show_info()

def volume_up():
    current_vol = mpc.status()['volume']
    if current_vol != "100":
        mpc.setvol(int(current_vol)+10)
        show_info()

def volume_down():
    current_vol = mpc.status()['volume']
    if current_vol != "0":
        mpc.setvol(int(current_vol)-10)
        show_info()


Arduino.pinMode(14, input)
lcd = Lcd([8,9,4,5,6,7],[16,2])

say_hello()

mpc = MPDClient()
mpc.connect("localhost", 6600)

init_playlist()

play()

while True:

    button = detect_button()
    mpc_state = mpc.status()['state']

    if button == "PLAY":
        if mpc_state == 'pause':
            play()
        elif mpc_state == 'play':
            pause()

    elif button == "NEXT":
        next()

    elif button == "PREV":
        previous()

    elif button == "VUP":
        volume_up()

    elif button == "VDOWN":
        volume_down()