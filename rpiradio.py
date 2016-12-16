#!/usr/bin/python2
# coding=utf-8
import os, time, re, threading
from nanpy import Arduino, Lcd
import rpiradio_conf as config
Arduino.pinMode(14, input)

lcd = Lcd([8,9,4,5,6,7],[16,2])            # Setup the LCD pins for the Sainsmart Shield

#playlist = config.PLAYLIST

max_trax = config.MAX_STATIONS

def hello():
   lcd.printString(16*" ", 0, 0)                                            # Send it out to the LCD Display
   lcd.printString("Raspberry Pi", 0, 0)
   lcd.printString(16*" ", 0, 1)
   lcd.printString("Internet Radio", 0, 1)

def getKey():                                    # Function to Translate the analogRead values from the Keys to a Command
   val = Arduino.analogRead(14)			 # It changes from shield to shield... So, you may need to configure it manually
   if val == 1023:
    return "NONE"
   elif val < 50:
    return "RIGHT"
   elif val < 250:
    return "UP"
   elif val < 300:
    return "DOWN"
   elif val < 500:
    return "LEFT"
   elif val < 700:
    return "SEL"
   else:
    return "KBD_FAULT"

def getTrack():					# Function to get info about stations from mpc and display it to LCD
   station = os.popen('mpc --wait --format "[%name%]" | head -n1').readlines()[0][0:15]
   if station == '\n' or station == '':									# mpc often tells '\n', but who knows...
     station = os.popen('mpc --wait').readlines()[0][7:23]
   track = os.popen('mpc --wait --format "[%title%]" | head -n1').readlines()[0][0:15]
   if track == '\n' or track == '':
     track = "No track info"

   if len(station) <= 16 and len(track) <= 16:
     lcd.printString(16*" ", 0, 0)                                            # Send it out to the LCD Display
     lcd.printString(station, 0, 0)
     lcd.printString(16*" ", 0, 1)
     lcd.printString(track, 0, 1)
   else:
     loopTrackName(station, track)
   
def loopTrackName(station, track):
   if station >= 16 and track >= 16:
     sym_start_station = 0
     sym_start_track = 0
     sym_end_station = 16								# 16 symbols max for display 16x2
     sym_end_track = 16
     while sym_end_station <= len(station) and sym_end_track <= len(track):
       lcd.printString(16*" ", 0, 0)                                            # Send it out to the LCD Display
       lcd.printString(station[sym_start_station:sym_end_station], 0, 0)
       lcd.printString(16*" ", 0, 1)
       lcd.printString(track[sym_start_track:sym_end_track], 0, 1)
       sym_start += 1
       sym_end += 1



def getTime():					# To update the current track name
    global is_getTime
    if is_getTime == 1:				# Если флаг-переменная = 1, то функция уже была запущена, и мы передаем ей флаг (текущее время = 0) для завершения ее цикла
       time_cur = 0
    else:					# Если нет, то текущее время = текущее время, запускаем цикл
       time_cur = time.time()
    is_getTime = 1				# Показываем, что цикл запущен
    while True:
      if time_cur == 0:				# если текущее время 0, значит, новый цикл был запущен, выходим из текущего цикла
        break
      time_last = time.time() - time_cur
      time.sleep(10)
      if int(time_last) > 60:
         getTrack()
         time_last = 0
         time_cur = time.time()



hello()
track_num = 1                                                     # Start off on Track number 1
os.system("mpc --wait play " + str(track_num))            # Tell the OS to Play it
global is_getTime
is_getTime = 0
getTrack()                                                            # Send the Track info to the LCD
threading._start_new_thread(getTime,())


while True:
    key = getKey()                                                    # Do something if a key was pressed
    if key == "RIGHT":
     track_num += 1
     if track_num > max_trax:			# Start the count from 1 again
	track_num = 1
     os.system("mpc --wait play " + str(track_num))
     getTrack()
     threading._start_new_thread(getTime,())
    elif key == "LEFT":
      track_num -= 1
      if track_num < 1:				# Go to the end of count in cycle...
	track_num = max_trax
      os.system("mpc --wait play " + str(track_num))
      getTrack()
    elif key == "SEL":
      time.sleep(0.5)				# If SELECT is pressed for a long time, then reset
      key = getKey()
      if key == "SEL":
        lcd.printString(16*" ", 0, 0)
        lcd.printString("RESETTING...", 0, 0)
        lcd.printString(16*" ", 0, 1)
	lcd.printString("Please wait", 0, 1)
        os.system("touch /tmp/radio.reset")
	time.sleep(15)
      pause_state = os.popen("mpc toggle | sed -n 2p").readlines()
      if "paused" in str(pause_state):					# Print "paused" to the LCD, if pressed paused. Print current station and continue, if pressed continue
	lcd.printString(16*" ", 0, 0)
	lcd.printString("-----PAUSED-----", 0, 0)
	lcd.printString(16*" ", 0, 1)
	lcd.printString("-------||-------", 0, 1)
      elif "playing" in str(pause_state):
	os.system("mpc play " + str(track_num))
	getTrack()
    elif key == "UP":
      vol_state = os.popen("mpc volume +10 | sed -n 3p | cut -d '%' -f1 | tr -d '\n'").readline()
      lcd.printString(16*" ", 0, 0)
      lcd.printString("   "+vol_state, 0, 0)
      lcd.printString(16*" ", 0, 1)
#      time.sleep(0.1)
      getTrack()
    elif key == "DOWN":
      vol_state = os.popen("mpc volume -10 | sed -n 3p | cut -d '%' -f1 | tr -d '\n'").readline()
      lcd.printString(16*" ", 0, 0)
      lcd.printString("    "+vol_state, 0, 0)
      lcd.printString(16*" ", 0, 1)
#      time.sleep(0.1)
      getTrack()

    elif key == "RESET":
#      vol_state = os.popen("mpc volume -10 | sed -n 3p | cut -d '%' -f1 | tr -d '\n'").readline()
      lcd.printString(16*" ", 0, 0)
      lcd.printString("reset", 0, 0)
      lcd.printString(16*" ", 0, 1)
#      time.sleep(0.1)
#      getTrack()
