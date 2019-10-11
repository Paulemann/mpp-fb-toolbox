#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#######################################################################################################################
#
#    Python prototype which logs on to a Fritz AVM 7390 and
#    extracts the number of sent and received bytes of
#    today, yesterday, last week and last month
#
#    Visit https://github.com/framps/pythonScriptCollection for latest code and other details
#
#######################################################################################################################
#
#    Copyright (C) 2013 framp at linux-tips-and-tricks dot de
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################################################################

import httplib
from xml.dom import minidom
import hashlib
import re
import sys
import os
import stat
import mimetypes
import socket
import fcntl
import struct

USER_AGENT="Mozilla/5.0 (U; Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0"

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def post_multipart(host, selector, fields, files):
    content_type, body = _encode_multipart_formdata(fields, files)
    h = httplib.HTTPConnection(host)
    headers = {
        #'User-Agent': 'python_multipart_caller',
        'User-Agent': USER_AGENT,
        'Content-Type': content_type,
        'Accept': '*/*'
        }
    h.request('POST', selector, body, headers)
    res = h.getresponse()
    return res.read()

def _encode_multipart_formdata(fields, files):
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, fd) in files:
        file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
        filename = fd.name.split('/')[-1]
        contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        L.append('--%s' % BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % contenttype)
        fd.seek(0)
        L.append('\r\n' + fd.read())
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def getPage(server, sid, page, port=80):

    conn = httplib.HTTPConnection(server+':'+str(port))

    headers = { "Accept" : "application/xml",
                "Content-Type" : "text/plain",
                "User-Agent" : USER_AGENT}

    pageWithSid=page+"?sid="+sid
    conn.request("GET", pageWithSid, '', headers)
    response = conn.getresponse()
    data = response.read()
    if response.status != 200:
        #print "%s %s" % (response.status, response.reason)
        #print data
        sys.exit(1)
    else:
        return data

def loginToServer(server,password,port=80):

    conn = httplib.HTTPConnection(server+':'+str(port))

    headers = { "Accept" : "application/xml",
                "Content-Type" : "text/plain",
                "User-Agent" : USER_AGENT}

    initialPage='/login_sid.lua'
    conn.request("GET", initialPage, '', headers)
    response = conn.getresponse()
    data = response.read()
    if response.status != 200:
        #print "%s %s" % (response.status, response.reason)
        #print data
        sys.exit(1)
    else:
        theXml = minidom.parseString(data)
        sidInfo = theXml.getElementsByTagName('SID')
        sid=sidInfo[0].firstChild.data
        if sid == "0000000000000000":
            challengeInfo = theXml.getElementsByTagName('Challenge')
            challenge=challengeInfo[0].firstChild.data
            challenge_bf = (challenge + '-' + password).decode('iso-8859-1').encode('utf-16le')
            m = hashlib.md5()
            m.update(challenge_bf)
            response_bf = challenge + '-' + m.hexdigest().lower()
        else:
            return sid

    headers = { "Accept" : "text/html,application/xhtml+xml,application/xml",
                "Content-Type" : "application/x-www-form-urlencoded",
                "User-Agent" : USER_AGENT}

    loginPage="/login_sid.lua?&response=" + response_bf
    conn.request("GET", loginPage, '', headers)
    response = conn.getresponse()
    data = response.read()
    if response.status != 200:
        #print "%s %s" % (response.status, response.reason)
        #print data
        sys.exit(1)
    else:
        sid = re.search('<SID>(.*?)</SID>', data).group(1)
        if sid == "0000000000000000":
            #print "ERROR - No SID received because of invalid password"
            sys.exit(1)
        return sid
