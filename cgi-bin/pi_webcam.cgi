#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import fcntl
import struct
from fb_toolbox import get_ip_address
from ConfigParser import ConfigParser


# Localization
btnBack   = 'Zurück'
btnUpdt   = 'Aktual.'
btnExit   = 'Beenden'
strTitle  = 'Webcam'


cfgFile = 'fb.cfg'

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    camTitle = config.get('webcam', 'title')
except:
    camTitle = ''

myIPAddr = get_ip_address('eth0')

camURL   = 'http://{}/cgi-bin/get_stream_hd.cgi'.format(myIPAddr)

# mime type / html header
#html_header = 'Content-type: text/xml\nConnection: close\nExpires: -1\n'
#html_header = 'Content-type: text/xml\nConnection: close\nExpires: -1\Refresh: 5; URL=SoftKey:Exit\n'
html_header = 'Content-type: text/xml\n'

# header and footer
#header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneImageFile>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneImageFile onAppFocusLost="SoftKey:Update">\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
footer = '</CiscoIPPhoneImageFile>'

# default soft keys
softKey = '\t<SoftKeyItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t\t<Position>{}</Position>\n\t</SoftKeyItem>'

outLine = '\t<URL>{}</URL>'

print html_header
print header.format(strTitle, camTitle)
print outLine.format(camURL)
print softKey.format(btnBack, 'SoftKey:Exit', 1)
print softKey.format(btnUpdt, 'Softkey:Update', 2)
#print softKey.format(btnExit, 'Init:Services', 3)
print footer
