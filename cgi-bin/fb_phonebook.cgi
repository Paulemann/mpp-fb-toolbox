#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import os
import xml.etree.ElementTree as ET

from ConfigParser import ConfigParser
from fb_toolbox import *

cfgFile = 'fb.cfg'

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    fbAddr = config.get('fritzbox', 'hostname')
    fbPwd  = config.get('fritzbox', 'password')
    pbName = config.get('phonebook', 'name')
except:
    fbAddr = 'fritz.box'
    fbPwd  = ''
    pbName = 'Telefonbuch'

sid = loginToServer(fbAddr, fbPwd)

if not sid:
    sys.exit(1)

number = ''
name   = ''
search = False
update = False
pbPage = 1

if 'QUERY_STRING' in os.environ:
    query_string = os.environ['QUERY_STRING']
    if query_string:
        SearchParams = [i.split('=') for i in query_string.split('&')] #parse query string
        for key, value in SearchParams:
            if key == 'search':
                search = False if value == '0' else True
            if key == 'update':
                update = False if value == '0' else True
            if key == 'number':
                number = str(value)
            if key == 'name':
                name = value
            if key == 'book':
                pbName = value
            if key == 'page':
                pbPage = int(value)

if update:
   number = ''
   name = ''

# Localization
btnBack        = 'Zurück'
btnCancel      = 'Abbruch'
btnDial        = 'Anrufen'
btnEdit        = 'Nummer bearb.'
btnExit        = 'Beenden'
btnNext        = 'Weiter'
btnSearch      = 'Suchen'
btnSelect      = 'Auswahl'
btnUpdate      = 'Aktual.'

srchPrefix     = 'In'
srchSuffix     = 'suchen'
srchName       = 'Name'
srchNumber     = 'Nummer'
srchPrompt     = 'Suchmuster eingeben'
srchResults    = 'Suchergebnisse'
srchItemsFound = 'Einträge gefunden'
srchItemFound  = 'Eintrag gefunden'

strSelUsr      = 'Kontakt für Anruf auswählen'
strPage        = 'Seite'
strOutOf       = 'von'
strMobile      = 'M'
strWork        = 'A'
strHome        = 'Z'


pbPath     = '/var/www/html'
pbFile     = '{}/{}.xml'.format(pbPath, pbName)

maxEntries = 32

myURL = 'http://{}/cgi-bin/{}?book={}'.format(get_ip_address('eth0'), os.path.basename(__file__), pbName)

# mime type / html header
html_header = 'Content-type: text/xml\n'

# header and footer
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneDirectory>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
footer = '</CiscoIPPhoneDirectory>'

# soft key
softKey = '\t<SoftKeyItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t\t<Position>{}</Position>\n\t</SoftKeyItem>'

outLine = '\t<DirectoryEntry>\n\t\t<Name>{}</Name>\n\t\t<Telephone>{}</Telephone>\n\t</DirectoryEntry>'


def fbpb_search():
    print html_header

    search = (
         '<CiscoIPPhoneInput>\n'
         '\t<Title>{} {} {}</Title>\n'
         '\t<Prompt>{}</Prompt>\n'
         '\t<URL>{}</URL>\n'
         '\t<InputItem>\n'
         '\t\t<DisplayName>{}</DisplayName>\n'
         '\t\t<QueryStringParam>number</QueryStringParam>\n'
         '\t\t<InputFlags>N</InputFlags>\n'
         '\t\t<DefaultValue></DefaultValue>\n'
         '\t</InputItem>\n'
         '\t<InputItem>\n'
         '\t\t<DisplayName>{}</DisplayName>\n'
         '\t\t<QueryStringParam>name</QueryStringParam>\n'
         '\t\t<InputFlags>L</InputFlags>\n'
         '\t\t<DefaultValue></DefaultValue>\n'
         '\t</InputItem>\n'
         '</CiscoIPPhoneInput>\n'
    ).format(srchPrefix, pbName, srchSuffix, srchPrompt, myURL, srchNumber, srchName)
    print search


def fbpb_export(server, sid, name):
    pbExport = post_multipart(server, '/cgi-bin/firmwarecfg', [('sid', str(sid)), ('PhonebookId', '0'), ('PhonebookExportName', name), ('PhonebookExport', '')], [])
    phonebooks = ET.fromstring(pbExport)

    if os.path.exists(pbFile):
        os.remove(pbFile)

    with open(pbFile, 'w') as xmlfile:
        xmlfile.write(header.format(pbName, strSelUsr) + '\n')
        for phonebook in phonebooks:
            if not phonebook.attrib['name'] == pbName:
                continue
            for contact in phonebook.iter('contact'):
                for element in contact:
                    if element.tag == 'person':
                        name = element.find('realName').text.strip().replace('&', '&amp;')
                        name = ' '.join(name.split())
                    if element.tag == 'telephony':
                        entries = len([num for num in element.iter('number') if num.text])
                        for num in element.iter('number'):
                            if num.text:
                                type = num.attrib['type'].replace('work', strWork).replace('home', strHome).replace('mobile', strMobile)
                                number = num.text
                                if entries > 1:
                                    xmlfile.write(outLine.format(name.encode('UTF-8') + ' (' + type.encode('UTF-8') + ')', number) + '\n')
                                else:
                                    xmlfile.write(outLine.format(name.encode('UTF-8'), number) + '\n')
        xmlfile.write(footer + '\n')


def fbpb_print(page):
    with open(pbFile, 'r') as xmlfile:
        lines = xmlfile.readlines()

    pages = (len(lines) - 5) / (maxEntries * 4) + 1

    if page > pages:
        page = pages
    elif page < 1:
        page = 1

    print html_header

    for i in range(3):
        print lines[i],

    print '\t<Prompt>{} {} {} {}</Prompt>\n'.format(strPage, page, strOutOf, pages),

    start = (page - 1) * maxEntries * 4 + 4
    end   = page * maxEntries * 4 + 3

    if end > (len(lines) - 2):
        end = len(lines) - 2
    if start < end:
        for i in range(start, end + 1):
            print lines[i],

    print softKey.format(btnDial, 'SoftKey:Dial', 1)
    print softKey.format(btnEdit, 'SoftKey:EditDial', 2)

    if page > 1:
        prev = page - 1
        print softKey.format(btnBack, myURL + '&amp;page=' + str(prev), 3)
    else:
        print softKey.format(btnUpdate, myURL + '&amp;update=1', 3)

    if page < pages:
        next = page + 1
        print softKey.format(btnNext, myURL + '&amp;page=' + str(next), 4)
    else:
        print softKey.format(btnSearch, myURL + '&amp;search=1', 4)

    print lines[-1]


def fbpb_match(number, name):
    with open(pbFile, 'r') as xmlfile:
        lines = xmlfile.readlines()

    matchNumber = []
    if number:
        expr = re.compile('<Telephone>.*{}.*</Telephone>'.format(number))
        for i, line in enumerate(lines):
            if expr.search(line):
                for j in range (i - 2, i + 2):
                    matchNumber.append(lines[j])

    matchName = []
    if name:
        expr = re.compile('<Name>.*{}.*</Name>'.format(name))
        if number and len(matchNumber) > 0:
            input = matchNumber
        else:
            input = lines
        for i, line in enumerate(input):
            if expr.search(line):
                for j in range (i - 1, i + 3):
                    matchName.append(input[j])

    if name and len(matchName) > 0:
        input = matchName
    else:
        input = matchNumber
    nItems = len(input) / 4

    print html_header
    print header.format(srchResults, str(nItems) + ' ' + (srchItemsFound if nItems > 1 else srchItemFound))
    for line in input:
        print line
    print softKey.format(btnDial, 'SoftKey:Dial', 1)
    print softKey.format(btnEdit, 'SoftKey:EditDial', 2)
    print footer


if update or not os.path.isfile(pbFile):
    pbExport = fbpb_export(fbAddr, sid, pbName)

if search:
    fbpb_search()
    exit()

if number or name:
    fbpb_match(number, name)
    exit()

fbpb_print(pbPage)
