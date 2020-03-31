# mpp-fb-toolbox
This is a collection of python scripts to be run from the cgi-bin directory of a python enabled web server to display information from your local AVM FRITZ!Box on a Cisco 8800 Series Multiplatform (aka MPP or 3PCC) Phone. For specific instructions related to the configuration of your web service and how to enable the exceution of python scripts, please consult the documentation of your specific software.
I had this successfully running with apache2 on a Raspberry Pi with a current install of Raspbian.  


Prerequisites:
==============
- Make sure the webserver has network connectvity to both your Cisco 8800 Series Phone and to your local FRITZ!Box.
- Setup and remember your credentials (password) to access the web ui of your local FRITZ!Box.
- The phonebook on your local FRITZ!Box must contain some entries and the answering machine (TAM) on you FRITZ!Box is configured and turned on.
- You must have configured a user (default ftpuser) and password  on your local FRITZ!Box to access the answering machine file via `ftp://<Your FRITZ!Box IP address>/FRITZ/voicebox/meta0`
- All required values must have been entered in the file fb.cfg located in the same directory as the script files.
- Make sure the script files are executable both locally and by the web service.
- Furthermore, you should be able to access the admin page and be familar with the basic setup of your Cisco 8800 Series Multiplatform Phone. 

Restrictions:
=============
- Currently the location where the phonebook and answering machines file are stored is hardcoded as `/tmp/`. If this path is not accessible or doesn't exist  you must edit the value of tmpPath or pbPath, respectively, in the files fb_phonebook.cgi and fb_tam.cgi. 

Improvements:
=============
- The structure of fb.cfg has been changed to allow the use of multiple phone books. Phone books are referenced by their owner/id: 0 = main phonebook, 1-239 = user defined phonebooks, 240-253 = online phonebooks, 255 = intern, 256 = clip info.
You must configure a name for each id which may differ from the name that's specified in the FRITZ!Box ui. 
- You may now configure multiple answering machines in fb.cfg under the new section [answering machine]. The configuration follows the same scheme as for the phone books. 
- In case you've configured your box to use a user name and password combo instead of password only for login you can now configure the user name in fb.cfg. 
- For those who store their voicebox files on external media, you can now configure the path in fb.cfg in the [answering machine] section. 

Optional:
=========
- If you have a webcam that can generate snapshots in jpeg format, a menu entry is added by configuration of the respective snapshot url to display the snapshot on the screen of your Cisco IP phone.
- It is not a strict prerequisite, but it makes sense that - prior to the installation of the scripts - you have setup the Cisco 8800 IP Phone to register as a SIP client at your local FRITZ!Box and you are able to make calls with your phone. See section "Setup Cisco 8800 Series Multiplatform Phone (MPP) with AVM FRITZ!Box" if you're looking for guidance on how to setup the phone.
- Added fb_phonebook.cgi.alphabet as an optional replacement for fb_phonebook.cgi. The alternativ script offers pagewise grouping of entries by starting letters. Additionally, you may jump from 1st to last page and vice versa (page rotation). To use ist, simply copy fb_phonebook.cgi.alphabet to fb_phonebook.cgi

Test the installation by entering `http://<Web server IP address>/cgi-bin/fb_services.cgi` in the address field of your brwoser. You should be able to see the XML code the script has generated. If not, you must troubleshoot your setup.


Configuration:
============== 
The configuration file fb.cfg must be created with the below data:

```
[fritzbox]
hostname: <Hostname or IP address of the FRITZ!Box; e.g. fritz.box or 192.168.178.1>
username: <User name to access the FRITZ!Box web ui - in case it's been configured, else empty>
password: <Password to access the FRITZ!Box web ui >

[phonebook]
names:    <Phonebook names, separated by comma if there are multiple; e.g. Telefonbuch, Telefonbuch 2>
ids:      <Phonebook ids, separated by comma if there are multiple; e.g. 0, 1>
areacode: <Optional: your own area code; will shorten the display of local numbers>

[answering machine]
path:     <Path to voicebox files; Default: 'FRITZ/voicebox'>
names:    <Answering machine names, separated by comma if there are multiple; e.g. Anrufbeantworter, AB 2>
ids:      <Answering machine ids, separated by comma if there are multiple; e.g. 0, 1>

[ftp]
user:     <User who can access the NAS directories of your FRITZ!Box via ftp, default: ftpuser>
password: <Password>

[webcam]
title:    <Optional: title of the webcam snapshots to be displayed>
url:      <URL for downloading the webcam snapshot, e.g.: http://1.1.1.1/snapshot>
user:     <webcam user>
password: <webcam password>
width:    <For 8851: 559; configure according to model and preference>
height:   <For 8851: 265; configure according to model and preference>
```

Phone setup:
============
Enter `http://<Phone IP address>/admin/advanced` in the address filed of your bowser (login as user "admin" if required) -> Voice -> Phone

Confgure the following settings in section XML Service (names can be adapted according to your preference):
In case you want to use a spefice phonebook only (with its id used as a parameter to ?book=):
```
XML Directory Service Name:	FRITZ!Box Phonebook
XML Directory Service URL:	http://<Web server IP address>/cgi-bin/fb_phonebook.cgi?book=1
```
or in case you want to access all available/configured phonebooks:
```
XML Directory Service Name:	FRITZ!Box Phonebooks
XML Directory Service URL:	http://<Web server IP address>/cgi-bin/fb_directory.cgi
```
```
XML Application Service Name:	FRITZ!Box Services
XML Application Service URL:	http://<Web server IP address>/cgi-bin/fb_services.cgi
```

# Setup Cisco 8800 Series Multiplatform Phone (MPP) with AVM FRITZ!Box

Prerequisites:
==============
- You should be able to access Cisco's web site and your CCO account must be authorized to download software (required to update firmware on the phone).
- A local TFTP service for provisioning of firmware and language files is available.
- The 8800 series phone has been set up as a new telephony device on the FRITZ!Box: FRITZ!Box  -> Telefonie -> Telefoniegeräte -> Neues Gerät einrichten)


Basic configuration:
====================
- Connect the 8800 series phone to the network and a power source (via PoE or power supply). The phone starts up.
- Assign a password (user password; not admin password!)
- Configure network settings: Settings -> Network configuration -> IPv4 address settings (DHCP oder static)
- Check network settings: Settings -> Status -> Network status

Further settings will be configured via browser (attention: only MS Internet Explorer/Edge seem to work reliably)


Update Firmware:
================
Enter `http://<Phone IP address>` in the browser address field and login as user "user" and previously assigned password -> Admin-Login (basic)

Info -> Status:
```
Product Information:
Software Version:    sip88xx.11-0-1MPP-477.loads (Beispiel)
```
- Visit software.cisco.com and look for updated firmware for IP Phone 88xx with Multiplatform Firmware
- Download Multiplatform Firmware e.g. `cmterm-88xx.11-2-3MSR1-1_REL.zip` and unpack files to directory on tftp server
- Download Multiplatform Firmware Locale Installer e.g. `cmterm-68xx_78xx_88xx.11-2-3MPP-398-Locale-1.zip` and extract the file `de-DE_88xx-11.2.3.1000.xml` (this is the German locale file; select accordingly for other languages). Copy the file as `de-DE.xml` to the directory `MPP` on the tftp server
- Go back to 88xx Webui: `http://<Phone IP address>` -> Login as user  "user" and previously assigned password -> Admin-Login (advanced)

Voice -> Provisioning:
```
Firmware Upgrade:
Upgrade Rule: tftp://<tftp server IP address>/<path>/sip88xx.11-2-3MSR1-1.loads
```
-> Submit

Alternativly, via browser URL:
`http://<Phone IP address>/admin/upgrade?tftp://<tftp server IP address>/<path>/sip88xx.11-2-3MSR1-1.loads`

The phone reboots automatically after update


Localization:
=============
`http://<phone IP address>` -> login as user "user" and previously assigne password  -> Admin-Login (advanced)

Voice -> Regional:
```
Time (example for CET Time Zone setting):
Time Zone: GMT+1:00
Daylight Saving Time Rule: start=3/-1/7/2;end=10/-1/7/2;save=1
Daylight Saving Time Enable: Yes

Language (example for German locale):
Dictionary Server Script: serv=tftp://<tftp server IP address>/MPP/;d1=German;l1=de-DE;x1=de-DE.xml
Language Selection: German
Locale: de-DE
```
-> Submit


Configuration:
==============
`http://<IP-Adresse>` -> login as user "user" and previously assigne password  -> Admin-Login (advanced)

Voice -> System
```
System Configuration:
Admin Password: <Change Password>
Phone-UI-User-Mode: Yes
```
-> Submit

Voice -> Phone
```
General:
Station Name: <Telefonnummer>
Voice Mail Numer: **600

Line Key 1: 
Extension: 1

Line Key 2 to 10 (Configure your speed dials):
Extension: Disabled
Extended Function: fnc=sd;ext=<Telefonnummer>@$PROXY;vid=1;nme=<Anzeigename>
```
-> Submit

Voice -> Ext1
```
General:
Line Enable: Yes

Call Feature Settings:
Mailbox ID: $USER
Voice Mail Server: $USER@<FRITZ!Box IP address>

Proxy and Registration:
Proxy: <FRITZ!Box IP address>

Subscriber Information:
Display Name: <Individual display name>
User Name: <FRITZ!Box telephony device user name>
Passsword: <FIRTZ!Box telephony device password>

Dial Plan:
Dial Plan: (**x|*xx|**xxx|[3469]11|0|00|[2-9]xxxxxx|1xxx[2-9]xxxxxxS0|xxxxxxxxxxxx.)
```
-> Submit

Voice -> User
```
Supplementary Services:
Time Format: 24hr
Date Format: day/month

Audio Compliance:
Compliant Standard: ETSI
```
-> Submit

Voice -> Ext 2 to Ext 10
```
General:
Line Enable: No
```
-> Submit


Read/Restore configuration from file:
=====================================
`http://<phone IP address>` -> login as user "user" and previously assigned password  -> Admin-Login (advanced)

Voice -> Provioning:
```
Configuration Profile:
Profile Rule: tftp://<tftp server IP address>/<path>/<file name>
```
-> Submit


Optional control via browser:
=============================
- Show (and save) current configuration:
`http://<Phone IP address>/admin/spacfg.xml`

- Read/Restore configuration from file:
`http://<Phone IP adddress>/admin/resync?tftp://<tftp server IP address>/<path>/<file name>`

- View log messages:
`http://<Phone IP address>/admin/log/messages`

- Reboot:
`http://<Phone IP address>/reboot`


Documentation:
==============
- Release Notes: https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cuipph/MPP/8800/firmware/11-2-3/p881_b_11_2_3.html
- Admin Guide: https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cuipph/MPP/8800/english/adminguide/p881_b_8800-mpp-ag.html
