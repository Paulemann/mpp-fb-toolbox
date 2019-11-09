#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from struct import *
from functools import partial
from collections import namedtuple
from datetime import datetime

import urllib
import re
import os

from ConfigParser import ConfigParser

error   = False

cfgFile = 'fb.cfg'

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    fbAddr     = config.get('fritzbox', 'hostname')
    fbFTPUsr   = config.get('ftp', 'user')
    fbFTPPwd   = config.get('ftp', 'password')
    pbName     = config.get('phonebook', 'name')
    pbAreaCode = config.get('phonebook', 'areacode')
except:
    error      = True

    fbAddr     = 'fritz.box'
    fbFTPUsr   = 'ftpuser'
    fbFTPPwd   = ''
    pbName     = 'Telefonbuch'
    pbAreaCode = ''


tamIndex       = 0

if 'QUERY_STRING' in os.environ:
    query_string = os.environ['QUERY_STRING']
    if query_string:
        SearchParams = [i.split('=') for i in query_string.split('&')] #parse query string
        for key, value in SearchParams:
            if key == 'index':
                tamIndex = int(value)

tmpPath        = '/tmp/'
tamFile        = tmpPath + 'meta' + str(tamIndex)
#pbPath         = '/var/www/html/'
pbPath         = tmpPath
pbList         = [ pbName ]


# Localization:
strTAM         = 'FRITZ!Box Anrufbeantworter ({})'.format(tamIndex + 1)
strNewMessages = ' neue Nachricht(en)'
strAnonymous   = 'Anonymer Anrufer'
strError       = 'Fehler'

btnExit        = 'Beenden'
btnDialTAM     = 'AB anrufen'
btnDialID      = 'Nr. wählen'

dictDayOfWeek  = {'Mon':'Mo', 'Tue':'Di', 'Wed':'Mi', 'Thu':'Do', 'Fri':'Fr', 'Sat':'Sa', 'Sun':'So'}


Message        = namedtuple('Message', 'datalength sequence reclength new callerID filename path day month year hours minutes seconds calledID')

recordSize     = 348
url            = 'ftp://{}:{}@{}/FRITZ/voicebox/meta0'.format(fbFTPUsr, fbFTPPwd, fbAddr)

messages = []
try:
    urllib.urlretrieve(url, tamFile)
    with open(tamFile, 'rb') as fin:
        for record in iter(partial(fin.read, recordSize), b''):
            message = Message._make(unpack('>2xHB18xB3xH23x15s57x15s17x60s68xBBBBBB30x10s18x', record))
            # Skip the following check if you want to see old messages, too
            if message.new > 0:
                messages.append(message)
except:
    error = True
    pass

newmsgs = len(messages)

mapping = []
try:
    for pbFile in pbList:
        with open(pbPath + pbFile + '.xml') as file:
             pb = file.read()
        mapping.extend(re.findall(r'<Name>(.*)</Name>\s*<Telephone>(.*)</Telephone>', pb))
except:
    pass

def outputLine(msg):
    dateStr = '{:02d}.{:02d}.{:02d}'.format(msg.day, msg.month, msg.year)
    DayOfWeek = datetime.strptime(dateStr, '%d.%m.%y').strftime('%a')
    locDayOfWeek = dictDayOfWeek[DayOfWeek]

    timeStr = '{:02d}:{:02d}'.format(msg.hours, msg.minutes)

    lenStr = '{:d}:{:02d}'.format(msg.reclength/60, msg.reclength%60)

    callerName = ''
    if msg.callerID:
        for name, number in mapping:
            if number in msg.callerID:
                callerName = name
        if callerName:
            callerID = callerName
        else:
            #callerID = msg.callerID.split(b'\0',1)[0]
            callerID = msg.callerID.rstrip('\0')
            if pbAreaCode:
                callerID = callerID.replace(pbAreaCode, '')
    else:
        callerID = strAnonymous

    Line = '\t<MenuItem>\n\t\t<Name>{} {} {}: {} ({})</Name>\n\t\t<URL>Dial:{}</URL>\n\t</MenuItem>'
    #Line = '\t<DirectoryEntry>\n\t\t<Name>{} {} {}: {} ({})</Name>\n\t\t<Telephone>{}</Telephone>\n\t</DirectoryEntry>'

    print Line.format(locDayOfWeek, dateStr, timeStr, callerID, lenStr, msg.callerID.rstrip('\0'))


# mime type / html header
html_header = 'Content-type: text/xml\n'

# header and footer
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneMenu>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
#header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneDirectory>\n\t<Title>{}</Title>\n\t<Prompt>{} {}</Prompt>'

footer = '</CiscoIPPhoneMenu>'
#footer = '</CiscoIPPhoneDirectory>'

softKey = '\t<SoftKeyItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t\t<Position>{}</Position>\n\t</SoftKeyItem>'

print html_header
if error:
    print header.format(strTAM, strError)
else:
    print header.format(strTAM, str(newmsgs) + strNewMessages)

# read messages in reverse order
for message in messages[::-1]:
    outputLine(message)

if newmsgs > 0:
    print softKey.format(btnDialID,'SoftKey:Select', 1)
print softKey.format(btnDialTAM, 'Dial:**60' + str(tamIndex), 2)
print softKey.format(btnExit, 'Init:Services', 3)

print footer
