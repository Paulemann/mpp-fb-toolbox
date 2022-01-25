#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import re
import os
import stat
import mimetypes
import socket
import fcntl
import struct

from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
from xml.etree.ElementTree import parse, dump
from time import sleep


_debug = False

USER_AGENT="Mozilla/5.0 (U; Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0"


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode('utf-8'))
    )[20:24])


def post_multipart(host, selector, fields, files):
    uri='http://' + host + selector

    content_type, body = _encode_multipart_formdata(fields, files)
    data = body.encode()

    headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': content_type,
        'Accept': '*/*'
        }

    req = Request(uri, data=data, headers=headers)

    try:
        with  urlopen(req) as response:
            ret = response.read()
    except (HTTPError, URLError) as e:
       return None

    return ret


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
        filename = os.path.split(fd.name)[1]
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


def loginToServer(ipaddr, user, password, port=80):
    uri = 'http://{}:{}/login_sid.lua'.format(ipaddr, port)
    hdr = {'User-Agent': USER_AGENT}

    req = Request(uri, headers=hdr)

    try:
        with urlopen(req) as response:
            dom = parse(response)
            sid = dom.findtext('./SID')
            challenge = dom.findtext('./Challenge')
    except (HTTPError, URLError) as e:
        if _debug:
            print(e)
        return None

    #if sid == '0000000000000000':
    retry = True
    while sid == '0000000000000000' and retry:
        md5 = hashlib.md5()
        md5.update(challenge.encode('utf-16le'))
        md5.update('-'.encode('utf-16le'))
        md5.update(password.encode('utf-16le'))

        resp = challenge + '-' + md5.hexdigest().lower()

        if user:
            data = urlencode({'username': user, 'response': resp}).encode()
        else:
            data = urlencode({'response': resp}).encode()

        try:
            with urlopen(req, data=data) as response:
                dom = parse(response)
                sid = dom.findtext('./SID')
                blocktime = int(dom.findtext('./BlockTime'))
                if sid == '0000000000000000' and blocktime > 0:
                    sleep(blocktime + 1)
                    if _debug:
                        dump(dom.getroot())
                        print('Block Time:', blocktime)
                else:
                    retry = False

        except (HTTPError, URLError) as e:
            if _debug:
                print(e)
            return None

    if _debug:
        dump(dom.getroot())
        print('Session ID:', sid)

    if sid == '0000000000000000':
        return None

    return sid


def getPage(ipaddr, sid, page, values=None, port=80):
    uri = 'http://{}:{}/{}'.format(ipaddr, port, page[1:] if page[0] == '/' else page)
    hdr = {'User-Agent': USER_AGENT}

    if not values:
        values = {}
    values['sid'] = sid

    data = urlencode(values).encode()

    req = Request(uri, data=data, headers=hdr)

    try:
        with urlopen(req) as response:
            page = response.read()
    except (HTTPError, URLError) as e:
        if _debug:
            print(e)
        return None

    return page
