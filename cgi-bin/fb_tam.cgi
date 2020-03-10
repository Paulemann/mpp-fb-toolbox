#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from struct import *
from functools import partial
from collections import namedtuple
from datetime import datetime
from tempfile import gettempdir

import urllib
import re
import os

from ConfigParser import ConfigParser


# Localization:
strTAM         = 'Anrufbeantworter'
strNewMessages = ' neue Nachricht(en)'
strAnonymous   = 'Anonymer Anrufer'
strError       = 'Fehler'

btnExit        = 'Beenden'
btnDialTAM     = 'AB anrufen'
btnDialID      = 'Nr. wählen'

dictDayOfWeek  = {'Mon':'Mo', 'Tue':'Di', 'Wed':'Mi', 'Thu':'Do', 'Fri':'Fr', 'Sat':'Sa', 'Sun':'So'}


cfgFile    = 'fb.cfg'
pbFileName = 'phonebook'

error      = False

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    fbAddr     = config.get('fritzbox', 'hostname')
    fbFTPUsr   = config.get('ftp', 'user')
    fbFTPPwd   = config.get('ftp', 'password')

    pbIds      = [int(id.strip()) for id in config.get('phonebook', 'ids').split(',')]
    pbAreaCode = config.get('phonebook', 'areacode')

    tamPath    = config.get('answering machine', 'path')
    tamNames   = [name.strip() for name in config.get('answering machine', 'names').split(',')]
    tamIds     = [int(id.strip()) for id in config.get('answering machine', 'ids').split(',')]
except:
    error      = True

    fbAddr     = 'fritz.box'
    fbFTPUsr   = 'ftpuser'
    fbFTPPwd   = ''

    pbIds      = [0]
    pbAreaCode = ''

    tamPath    = 'FRITZ/voicebox'
    tamNames   = [strTAM]
    tamIds     = [0]

tamId          = 0

if 'QUERY_STRING' in os.environ:
    query_string = os.environ['QUERY_STRING']
    if query_string:
        SearchParams = [i.split('=') for i in query_string.split('&')] #parse query string
        for key, value in SearchParams:
            if key == 'index':
                tamId = int(value)

strTAMTitle    = 'FRITZ!Box {}'.format(tamNames[tamIds.index(tamId)])

Message        = namedtuple('Message', 'datalength sequence type filelength reclength new callerID filename path day month year hours minutes seconds calledID')
recordSize     = 348

#url            = 'ftp://{}:{}@{}/FRITZ/voicebox/meta{}'.format(fbFTPUsr, fbFTPPwd, fbAddr, tamId)
url            = 'ftp://{}:{}@{}/{}/meta{}'.format(fbFTPUsr, fbFTPPwd, fbAddr, tamPath, tamId)

tmpPath        = gettempdir()
tamFile        = os.path.join(tmpPath, 'meta' + str(tamId))
pbList         = [ pbFileName ] if 0 in pbIds else []

try:
    pbList.extend([ pbFileName + '{}'.format(id + 1) for id in pbIds if id > 0 ])
except:
    pass

messages = []
try:
    urllib.urlretrieve(url, tamFile)
    with open(tamFile, 'rb') as fin:
        for record in iter(partial(fin.read, recordSize), b''):
            # Byte order
            if record[0] == '\x5c':
                byteOrder = '<'   # little-endian (eg. 7530)
            else:
                byteOrder = '>'   # big-endian (e.g. 7390,7490,7590)
            message = Message._make(unpack(byteOrder + 'III4xIII24x15s57x15s17x60s68xBBBBBB30x10s18x', record))
            # Skip the following check if you want to see old messages, too
            if message.new > 0:
                messages.append(message)

            #print "[000:003] Datalength: ", message.datalength  # Unsigned Integer (4 Bytes): 384                          I
            #print "[004:007] Sequence:   ", message.sequence    # Unsigned Integer:                                        I
            #print "[008:011] Type:       ", message.type        # Unsigned Integer, follwoed by 4 Bytes:                   I4x
            #print "[016:019] Filelenth:  ", message.filelength  # Unsigned Integer:                                        I
            #print "[020:023] Reclength:  ", message.reclength   # Unsigned Integer:                                        I
            #print "[024:027] New:        ", message.new         # Unsigned Integer, followed by 24 Bytes:                  I24x
            #print "[052:066] CallerID:   ", message.callerID    # String of 15 Bytes followed by 57 Bytes:                 15s57x
            #print "[124:138] Filename:   ", message.filename    # String of 15 Bytes followed by 17 Bytes:                 15s17x
            #print "[156:215] Path:       ", message.path        # String of 60 Bytes followed by 68 Bytes:                 60s68x
            #print "[284:284] Day:        ", message.day         # Unsigned Char (1 Byte):                                  B
            #print "[285:285] Month:      ", message.month       # Unsigned Char (1 Byte):                                  B
            #print "[286:286] Year:       ", message.year        # Unsigned Char (1 Byte):                                  B
            #print "[287:287] Hours:      ", message.hours       # Unsigned Char (1 Byte):                                  B
            #print "[288:288] Minutes:    ", message.minutes     # Unsigned Char (1 Byte):                                  B
            #print "[289:289] Seconds:    ", message.seconds     # Unsigned Char (1 Byte) followed by 30 Bytes:             B30x
            #print "[320:329] CalledID:   ", message.calledID    # String of 10 Bytes followed by 18 Bytes:                 10s18x
except:
    error = True
    pass

newmsgs = len(messages)

mapping = []
try:
    for pbFile in pbList:
        with open(os.path.join(tmpPath, pbFile + '.xml')) as file:
             pb = file.read()
        mapping.extend(re.findall(r'<Name>(.*)</Name>\s*<Telephone>(.*)</Telephone>', pb))
except:
    pass

def outputLine(msg):
    dateStr = '{:02d}.{:02d}.{:02d}'.format(msg.day, msg.month, msg.year)
    DayOfWeek = datetime.strptime(dateStr, '%d.%m.%y').strftime('%a')
    locDayOfWeek = dictDayOfWeek[DayOfWeek]

    timeStr = '{:02d}:{:02d}'.format(msg.hours, msg.minutes)
    lenStr  = '{:d}:{:02d}'.format(msg.reclength/60, msg.reclength%60)

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
    print header.format(strTAMTitle, strError)
else:
    print header.format(strTAMTitle, str(newmsgs) + strNewMessages)

# read messages in reverse order
for message in messages[::-1]:
    outputLine(message)

if newmsgs > 0:
    print softKey.format(btnDialID,'SoftKey:Select', 1)
print softKey.format(btnDialTAM, 'Dial:**60' + str(tamId), 2)
print softKey.format(btnExit, 'Init:Services', 3)

print footer
