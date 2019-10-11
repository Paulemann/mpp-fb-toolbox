#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import fcntl
import struct
from fb_toolbox import get_ip_address
from ConfigParser import ConfigParser

cfgFile = 'fb.cfg'

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    pbName = config.get('phonebook', 'name')
except:
    pbName = 'Telefonbuch'

# Localization
strTitle  = 'FRITZ!Box Telefonbuch'
strPrompt = ''

url = 'http://{}/cgi-bin/fb_phonebook.cgi?book={}'.format(get_ip_address('eth0'), pbName)

# mime type / html header
html_header = 'Content-type: text/xml\n'

# header and footer
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneMenu>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
footer = '</CiscoIPPhoneMenu>'

outLine = '\t<MenuItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t</MenuItem>'

print html_header
print header.format(strTitle, strPrompt)
print outLine.format(pbName, url)
print footer
