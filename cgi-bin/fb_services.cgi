#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import fcntl
import struct
from fb_toolbox import get_ip_address

myIPAddr = get_ip_address('eth0')

# Localization
itemTAM         = 'Anrufbeantworter'
itemInCalls     = 'Ankommende Anrufe'
itemOutCalls    = 'Ausgehende Anrufe'
itemMissedCalls = 'Anrufe in Abwesenheit'
itemWebCam      = 'Webcam Schnappschuß'

strTitle  = 'FRITZ!Box Dienste'
strPrompt = ''

# mime type / html header
html_header = 'Content-type: text/xml\n'

# header and footer
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneMenu>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
footer = '</CiscoIPPhoneMenu>'

outLine = '\t<MenuItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t</MenuItem>'

print html_header
print header.format(strTitle, strPrompt)

print outLine.format(itemTAM, 'http://{}/cgi-bin/fb_tam.cgi'.format(myIPAddr))
print outLine.format(itemInCalls, 'http://{}/cgi-bin/fb_calls.cgi?type=1'.format(myIPAddr))
print outLine.format(itemOutCalls, 'http://{}/cgi-bin/fb_calls.cgi?type=4'.format(myIPAddr))
print outLine.format(itemMissedCalls, 'http://{}/cgi-bin/fb_calls.cgi?type=2'.format(myIPAddr))
print outLine.format(itemWebCam, 'http://{}/cgi-bin/pi_webcam.cgi'.format(myIPAddr))

print footer
