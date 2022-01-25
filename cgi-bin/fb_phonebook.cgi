#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os
import xml.etree.ElementTree as ET

from collections import Counter
from string import ascii_uppercase

from tempfile import gettempdir
from configparser import ConfigParser
from fb_toolbox import *


# Localization
btnCancel      = 'Abbruch'
btnDial        = 'Anrufen'
btnEdit        = 'Nummer bearb.'
btnExit        = 'Beenden'
btnBack        = 'Zurück'
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
strEntries     = 'Einträge'
strPage        = 'Seite'
strOutOf       = 'von'
strMobile      = 'M'
strWork        = 'A'
strHome        = 'Z'
strError       = 'Fehler'

strPhoneBook   = 'Telefonbuch'

cfgFile    = 'fb.cfg'
maxEntries = 32

# mime type / html header
html_header = 'Content-type: text/xml\n'

# header and footer
header = '<?xml version="1.0" encoding="UTF-8"?>\n<CiscoIPPhoneDirectory>\n\t<Title>{}</Title>\n\t<Prompt>{}</Prompt>'
footer = '</CiscoIPPhoneDirectory>'

# soft key
softKey = '\t<SoftKeyItem>\n\t\t<Name>{}</Name>\n\t\t<URL>{}</URL>\n\t\t<Position>{}</Position>\n\t</SoftKeyItem>'

# error descriptions
errMismatch = 'Die Zahl der Telefonbuchnamen ({}) enstpricht nicht der Zahl der Indices ({}).'
errMalQuery = 'Ungültiges Format der Anfrage ({}).'
errNoSID    = 'Keine gültige Session ID.'
errConfig   = 'Konfiguration ungültig oder nicht gefunden.'


def main():
    global pbName, pbId, myURL

    number     = ''
    name       = ''
    search     = False
    update     = False

    pbPage     = 0
    pbId       = 0
    pbFileName = 'phonebook'

    try:
        # Read the config file
        config = ConfigParser()
        config.read([os.path.abspath(cfgFile)])

        fbAddr  = config.get('fritzbox', 'hostname')
        fbUsr   = config.get('fritzbox', 'username')
        fbPwd   = config.get('fritzbox', 'password')
        pbNames = [n.strip() for n in config.get('phonebook', 'names').split(',')]
        pbIds   = [int(id.strip()) for id in config.get('phonebook', 'ids').split(',')]
    except:
        fbpb_error(errConfig)

    if len(pbNames) != len(pbIds):
        fbpb_error(errMismatch.format(len(pbNames), len(pbIds)))

    if 'QUERY_STRING' in os.environ:
        query_string = os.environ['QUERY_STRING']
        if query_string:
            SearchParams = [i.split('=') for i in query_string.split('&')] #parse query string
            try:
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
                        pbId = int(value)
                        if pbId not in pbIds:
                            pbId = pbIds[0]
                    if key == 'page':
                        pbPage = int(value)
            except:
                fbpb_error(errMalQuery.format(query_string))

    if update or pbPage > 0:
        number = ''
        name = ''

    if pbPage == 0 and not number and not name:
        pbPage = 1

    if pbId > 0:
        pbFileName = pbFileName + str(pbId + 1)

    tmpPath = gettempdir()
    pbFile  = os.path.join(tmpPath, pbFileName + '.xml')

    pbName  = pbNames[pbIds.index(pbId)]
    myURL = 'http://{}/cgi-bin/{}?book={}'.format(get_ip_address('eth0'), os.path.basename(__file__), pbId)

    if update or not os.path.exists(pbFile):
        try:
            sid = loginToServer(fbAddr, fbUsr, fbPwd)
        except:
            sid = 0

        if not sid:
            fbpb_error(errNoSID)
            return
        else:
            if os.path.exists(pbFile):
                os.remove(pbFile)

            pb = fbpb_create(fbAddr, sid, pbFile)
    else:
        pb = fbpb_open(pbFile)

    pbPageInfo = fbpb_analyze(pb)

    if search:
        fbpb_search()
        exit()

    if number or name:
        fbpb_match(pb, number, name)
        exit()

    fbpb_print(pb, pbPage, pbPageInfo)


def fbpb_error(message):
    print(html_header)

    print(header.format(strError, message))
    print(footer)

    #sys.exit(1)


def fbpb_search():
    print(html_header)

    search = (
         '<CiscoIPPhoneInput>\n'
         '\t<Title>{} {} {}</Title>\n'
         '\t<Prompt>{}</Prompt>\n'
         '\t<URL>{}</URL>\n'
         '\t<InputItem>\n'
         '\t\t<DisplayName>{}</DisplayName>\n'
         '\t\t<QueryStringParam>number</QueryStringParam>\n'
         '\t\t<InputFlags>T</InputFlags>\n'
         '\t\t<DefaultValue></DefaultValue>\n'
         '\t</InputItem>\n'
         '\t<InputItem>\n'
         '\t\t<DisplayName>{}</DisplayName>\n'
         '\t\t<QueryStringParam>name</QueryStringParam>\n'
         '\t\t<InputFlags>A</InputFlags>\n'
         '\t\t<DefaultValue></DefaultValue>\n'
         '\t</InputItem>\n'
         '</CiscoIPPhoneInput>\n'
    ).format(srchPrefix, pbName, srchSuffix, srchPrompt, myURL, srchNumber, srchName)
    print(search)


def fbpb_create(server, sid, fname):
    outLine = '\t<DirectoryEntry>\n\t\t<Name>{}</Name>\n\t\t<Telephone>{}</Telephone>\n\t</DirectoryEntry>'

    pbExport = post_multipart(server, '/cgi-bin/firmwarecfg', [('sid', str(sid)), ('PhonebookId', str(pbId)), ('PhonebookExportName', pbName), ('PhonebookExport', '')], [])

    if not pbExport:
       return None

    phonebooks = ET.fromstring(pbExport)
    phonebook = phonebooks[0]

    data = [line + '\n' for line in header.format(pbName, strSelUsr).split('\n')]
    for contact in phonebook.iter('contact'):
        for element in contact:
            if element.tag == 'person':
                name = element.find('realName').text.strip().replace('&', '&amp;')
                name = ' '.join(name.split())
            if element.tag == 'telephony':
                entries = len([num for num in element.iter('number') if num.text])
                for num in element.iter('number'):
                    if 'type' in num.attrib and num.text:
                        type = num.attrib['type'].replace('work', strWork).replace('home', strHome).replace('mobile', strMobile)
                        number = num.text
                        if entries > 1:
                            data.extend([line + '\n' for line in outLine.format(name + ' (' + type + ')', number).split('\n')])
                        else:
                            data.extend([line + '\n' for line in outLine.format(name, number).split('\n')])
    data.append(footer + '\n')

    with open(fname, 'w') as xmlfile:
        xmlfile.writelines(data)

    return data


def fbpb_analyze(data):
    pages   = []
    mapping = {ord('ß'): 'ss', ord('ä'): 'ae', ord('ö'): 'oe', ord('ü'): 'ue', ord('Ä'): 'Ae', ord('Ö'): 'Oe', ord('Ü'): 'Ue'}

    numof  = dict.fromkeys(ascii_uppercase, 0)
    pb     = ET.fromstring(''.join(data))

    names  = []
    for entry in pb.findall('DirectoryEntry'):
        name = str(entry.find('Name').text).translate(mapping)
        names.append(name)
        numof[name[0].upper()] += 1

    pos  = 0
    page = {}
    page['entries']   = 0
    page['first'] = names[0][:2]
    page['last']  = names[0][:2]

    for letter in sorted(numof.keys()):
        if (page['entries'] + numof[letter]) <= maxEntries:
            page['entries'] += numof[letter]
            pos += numof[letter]
            page['last'] = names[pos - 1][:2] # letter
        else:
            if numof[letter] > maxEntries:
                for p in range(int(numof[letter]/maxEntries)):
                    numof[letter] -= maxEntries - page['entries']
                    page['entries'] = maxEntries
                    pos += maxEntries
                    page['last'] = names[pos-1][:2] # letter
                    pages.append(page.copy())
            else:
                pages.append(page.copy())
            page['first'] = names[pos][:2] # letter
            page['entries'] = numof[letter]
            pos += numof[letter]
            page['last'] = names[pos - 1][:2] # letter
    pages.append(page)

    return pages


def fbpb_open(fname):
    with open(fname, 'r') as xmlfile:
        data = xmlfile.readlines()

    return data


def fbpb_print(data, page, info):
    pages = len(info)

    if page > pages:
        page = pages
    elif page < 1:
        page = 1

    print(html_header)

    for i in range(3):
        print(data[i], end=' ')

    print('\t<Prompt>{} {} - {}</Prompt>\n'.format(strEntries, info[page - 1]['first'], info[page - 1]['last']), end=' ')

    start = 4
    for i in range(page - 1):
        start += info[i]['entries'] * 4
    end = start + info[page - 1]['entries'] * 4 - 1

    if end > (len(data) - 2):
        end = len(data) - 2
    if start < end:
        for i in range(start, end + 1):
            print(data[i], end=' ')

    print(softKey.format(btnDial, 'SoftKey:Dial', 1))

    prev = page - 1
    next = page % pages + 1

    if prev and page < pages:
        p2 = prev
        p3 = next
    else:
        p2 = next
        p3 = next % pages + 1

    if pages > 1:
        p2Range = info[p2 - 1]['first'] + ' - ' + info[p2]['last']
        print(softKey.format(p2Range, myURL + '&amp;page=' + str(p2), 2))

    if pages > 2:
        p3Range = info[p3 - 1]['first'] + ' - ' + info[p3 - 1]['last']
        print(softKey.format(p3Range, myURL + '&amp;page=' + str(p3), 3))

    print(softKey.format(btnEdit, 'SoftKey:EditDial', 4))
    print(softKey.format(btnSearch, myURL + '&amp;search=1', 5))
    print(softKey.format(btnUpdate, myURL + '&amp;update=1', 6))

    print(data[-1], end=' ')


def fbpb_match(data, number, name):
    matchNumber = []
    if number:
        expr = re.compile('<Telephone>.*{}.*</Telephone>'.format(number))
        for i, line in enumerate(data):
            if expr.search(line):
                for j in range (i - 2, i + 2):
                    matchNumber.append(data[j])

    matchName = []
    if name:
        expr = re.compile('<Name>.*{}.*</Name>'.format(name))
        if number and len(matchNumber) > 0:
            input = matchNumber
        else:
            input = data
        for i, line in enumerate(input):
            if expr.search(line):
                for j in range (i - 1, i + 3):
                    matchName.append(input[j])

    if name and len(matchName) > 0:
        input = matchName
    else:
        input = matchNumber
    nItems = len(input) / 4

    print(html_header)
    print(header.format(srchResults, str(nItems) + ' ' + (srchItemsFound if nItems > 1 else srchItemFound)))
    for line in input:
        print(line)
    print(softKey.format(btnDial, 'SoftKey:Dial', 1))
    print(softKey.format(btnEdit, 'SoftKey:EditDial', 2))
    print(footer)


if __name__ == "__main__":
    main()
