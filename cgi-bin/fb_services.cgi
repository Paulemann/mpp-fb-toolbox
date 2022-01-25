#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import socket
import fcntl
import struct
from fb_toolbox import get_ip_address
from configparser import ConfigParser


# Localization
itemInCalls     = 'Ankommende Anrufe'
itemOutCalls    = 'Ausgehende Anrufe'
itemMissedCalls = 'Anrufe in Abwesenheit'
itemWeather     = 'Wetter'
itemWebCam      = 'Webcam Schnappschuß'

strTAM          = 'Anrufbeantworter'

strSvcTitle     = 'FRITZ!Box Dienste'
strSvcPrompt    = ''


cfgFile = 'fb.cfg'

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    tamNames = [name.strip() for name in config.get('answering machine', 'names').split(',')]
    tamIds   = [int(id.strip()) for id in config.get('answering machine', 'ids').split(',')]
    camTitle = config.get('webcam', 'title')
except:
    tamNames = [strTAM]
    tamIds   = [0]
    camTitle = ''

if len(tamNames) != len(tamIds):
    sys.exit(1)

myIPAddr = get_ip_address('eth0')

# mime type / html header
html_header = 'Content-type: text/xml\n'

# header and footer
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneMenu>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
footer = '</CiscoIPPhoneMenu>'

outLine = '\t<MenuItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t</MenuItem>'

print(html_header)
print(header.format(strSvcTitle, strSvcPrompt))

for tamId in tamIds:
    tamName = tamNames[tamIds.index(tamId)]
    print(outLine.format(tamName, 'http://{}/cgi-bin/fb_tam.cgi?index={}'.format(myIPAddr, tamId)))
print(outLine.format(itemInCalls, 'http://{}/cgi-bin/fb_calls.cgi?type=1'.format(myIPAddr)))
print(outLine.format(itemOutCalls, 'http://{}/cgi-bin/fb_calls.cgi?type=4'.format(myIPAddr)))
print(outLine.format(itemMissedCalls, 'http://{}/cgi-bin/fb_calls.cgi?type=2'.format(myIPAddr)))
print(outLine.format(itemWeather, 'http://{}/cgi-bin/pi_weather.cgi'.format(myIPAddr)))
if camTitle:
    print(outLine.format(itemWebCam, 'http://{}/cgi-bin/pi_webcam.cgi'.format(myIPAddr)))

print(footer)
