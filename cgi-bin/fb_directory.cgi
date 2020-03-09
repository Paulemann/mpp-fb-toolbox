#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import fcntl
import struct
from fb_toolbox import get_ip_address
from ConfigParser import ConfigParser


# Localization
strPhoneBook = 'Telefonbuch'
strPBTitle   = 'FRITZ!Box {}'.format(strPhoneBook)
strPBPrompt  = ''


cfgFile = 'fb.cfg'

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    pbNames = [name.strip() for name in config.get('phonebook', 'names').split(',')]
    pbIds   = [int(id.strip()) for id in config.get('phonebook', 'ids').split(',')]
except:
    pbNames = [strPhoneBook]
    pbIds   = [0]

url = 'http://{}/cgi-bin/fb_phonebook.cgi?book={{}}'.format(get_ip_address('eth0'))

# mime type / html header
html_header = 'Content-type: text/xml\n'

# header and footer
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneMenu>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
footer = '</CiscoIPPhoneMenu>'

outLine = '\t<MenuItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t</MenuItem>'

print html_header
print header.format(strPBTitle, strPBPrompt)
for pbId in pbIds:
    pbName  = pbNames[pbIds.index(pbId)]
    print outLine.format(pbName, url.format(pbId))
print footer
