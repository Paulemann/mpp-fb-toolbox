#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from configparser import ConfigParser
from fb_toolbox import *


# Localization
btnDial   = 'Anrufen'
btnExit   = 'Beenden'
strTitle  = 'FRITZ!Box Anrufliste'
lstPrompt = ['Ankommende Anrufe', 'Anrufe in Abwesenheit', 'Abgelehnte Anrufe', 'Ausgehende Anrufe']

#1      Ankommender Anruf
#2      Anruf in Abwesenheit
#3      Der Anruf wurde abgelehnt. In der FRITZ!Box war zum Zeitpunkt des Anrufs eine Rufsperre für die Rufnummer des Anrufers eingerichtet oder Sie haben am Telefon die$
#4      Ausgehender Anruf
#5      Ankommender Anruf. Das Gespräch war noch nicht beendet, als die Anrufliste gesichert wurde.
#6      Ausgehender Anruf. Das Gespräch war noch nicht beendet, als die Anrufliste gesichert wurde.


cfgFile = 'fb.cfg'

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    fbAddr = config.get('fritzbox', 'hostname')
    fbUsr  = config.get('fritzbox', 'username')
    fbPwd  = config.get('fritzbox', 'password')
except:
    fbAddr = 'fritz.box'
    fbUsr  = ''
    fbPwd  = ''

sid = loginToServer(fbAddr, fbUsr, fbPwd)

if not sid:
    sys.exit(1)

type = 2

if 'QUERY_STRING' in os.environ:
    query_string = os.environ['QUERY_STRING']
    if query_string:
        SearchParams = [i.split('=') for i in query_string.split('&')] #parse query string
        for key, value in SearchParams:
            if key == 'type':
                type = int(value)

strPrompt = lstPrompt[ type - 1 ]

page = getPage(fbAddr, sid, '/fon_num/foncalls_list.lua', values={'csv': ''}).decode()

# mime type / html header
html_header = 'Content-type: text/xml\n'

# header and footer
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneMenu>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
footer = '</CiscoIPPhoneMenu>'

softKey = '\t<SoftKeyItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t\t<Position>{}</Position>\n\t</SoftKeyItem>'
outLine = '\t<MenuItem>\n\t\t<Name>{}: {}</Name>\n\t\t<URL>Dial:{}</URL>\n\t</MenuItem>'

print(html_header)
print(header.format(strTitle, strPrompt))

for line in page.split('\n'):
    try:
        calltype, timestamp, callerName, callerID, extension, calledID, duration  = line.split(';')
    except:
        continue

    if calltype == str(type):
        if callerName:
            print(outLine.format(timestamp, callerName.replace('&', '&amp;'), callerID))
        else:
            print(outLine.format(timestamp, callerID, callerID))

print(softKey.format(btnDial, 'SoftKey:Select', 1))
print(softKey.format(btnExit, 'Init:Services', 3))

print(footer)
