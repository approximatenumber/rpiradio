#!/usr/bin/env python2

import time
import netifaces
from nanpy import Arduino, Lcd
import urllib2
import sys

def show_info(first_msg, second_msg):
    lcd.printString(16*" ", 0, 0)
    lcd.printString(16*" ", 0, 1)
    lcd.printString(first_msg, 0, 0)
    lcd.printString(second_msg, 0, 1)


def check_ifaces():
    show_info("Checking i-faces", "and their IPs")
    time.sleep(2)

    for iface in netifaces.interfaces():

        try:
            ip = netifaces.ifaddresses(iface)[2][0]['addr']
            show_info(iface, ip)
            time.sleep(2)
        
        except KeyError:
            show_info(iface, "not configured")
            time.sleep(2)


def check_inet():
    show_info("Checking inet", "connection")
    time.sleep(1)

    if is_online() is True:
        show_info("We are", "ONLINE")
        sys.exit(0)
    elif is_online() is False:
        show_info("We are", "OFFLINE")
        sys.exit(1)


def is_online():
    try:
        urllib2.urlopen('http://google.com', timeout=1)
        True
    except urllib2.URLError as err: 
        return False



Arduino.pinMode(14, input)
lcd = Lcd([8,9,4,5,6,7],[16,2])

check_ifaces()

check_inet()