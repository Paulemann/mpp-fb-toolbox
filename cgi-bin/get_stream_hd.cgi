#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import os
import sys
from io import BytesIO
from PIL import Image, ImageOps
from ConfigParser import ConfigParser

cfgFile = 'fb.cfg'

try:
    # Read the config file
    config = ConfigParser()
    config.read([os.path.abspath(cfgFile)])

    camUrl    = config.get('webcam', 'url')
    camUsr    = config.get('webcam', 'user')
    camPwd    = config.get('webcam', 'password')
    imgWidth  = int(config.get('webcam', 'width'))
    imgHeight = int(config.get('webcam', 'height'))
except:
    sys.exit(1)

opener = None

def get_snapshot(url, username, password):
    global opener

    if not opener:
        passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwd_mgr.add_password(None, url, username, password)

        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPBasicAuthHandler(passwd_mgr))
        opener.add_handler(urllib2.HTTPDigestAuthHandler(passwd_mgr))

    request = urllib2.Request(url)
    imgData = opener.open(request).read()

    return imgData

imgSize = imgWidth, imgHeight

html_header = 'Content-Type: image/png\n'

jpgData = get_snapshot(camUrl, camUsr, camPwd)

image = Image.open(BytesIO(jpgData))

#image = image.resize(imgSize, Image.ANTIALIAS)
image = ImageOps.fit(image, imgSize, Image.ANTIALIAS)

with BytesIO() as output:
    image.save(output, format='PNG')
    contents = output.getvalue()

print html_header
print contents
