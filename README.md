# mpp-fb-toolbox
his is a collection of python scripts to be run from the cgi-bin directory of a python enabled web server to display information from your local AVM FRITZ!Box on a Cisco 8800 Series Multiplatform (aka MPP or 3PCC) Phone. For specific instructions related to the configuration of your web service and how to enable the exceution of python scripts, please consult the documentation of your specific software.
I had this successfully running with apache2 on a Raspberry Pi with a current install of Raspbian.  
Furthermore, you should be able to access the admin page and be familar with the basic setup of your Cisco 8800 Series Multiplatform Phone. 

Prerequisites:
==============
• Make sure the webserver has network connectvity to both your Cisco 8800 Series Phone and to your local FRITZ!Box.
• Setup and remember your credentials (password) to access the web ui of your local FRITZ!Box.
• The phonebook on your local FRITZ!Box must contain some entries and the answering machine (TAM) on you FRITZ!Box is configured and turned on.
• You must have configured a user (default ftpuser) and password  on your local FRITZ!Box to access the answering machine file via ftp://<your FRITZ!Box ip addess>/FRITZ/voicebox/meta0
• All required values must have been entered in the file fb.cfg located in the same directory as the script files.
• Make sure the script files are executable both locally and by the web service.


Restrictions:
=============
• Currently the location where the phonebook and answering machines file are stored is hardcoded as '/tmp/'. If this path is not accessible or doesn't exist  you must edit the value of tmpPath or pbPath, respectively, in the files fb_phonebook.cgi and fb_tam.cgi. 
• Without further adaptions, only one (the first) answering machine is supported. If you have multiple answering machines configured, you must edit the fb_services.cgi script file. There are two (currently inactive) lines that will display the respective menu entry and new messages for a second answering machine. You'll easily recognize the scheme to add more answering machines. I intend to make this configurable in fb.cfg to avoid manual editing of the scripts in the future.  


Optional:
=========
• If you have a webcam that can generate snapshots in jpeg format, a menu entry is added by configuration of the respective snapshot url to display the snapshot on the screen of your Cisco IP phone.
• It is not a strict prerequisite, but it makes sense that - prior to the installation of the scripts - you have setup the Cisco 8800 IP Phone to register as a SIP client at your local FRITZ!Box and you are able to make calls with your phone.

Test the installation by entering http://<web server ip address>/cgi-bin/fb_services.cgi in the address field of your brwoser. You should be able to see the XML code the script has generated. If not, you must troubleshoot your setup.


Configuration:
============== 
The configuratuion file fb.cfg must be configured with the below data:

[fritzbox]
hostname: <Hostname or IP address of the FRITZ!Box; e.g. fritz.box or 192.168.178.1>
password: <Password to acces the FRITZ!Box web ui >

[phonebook]
name: <Phoenbook name; e.g. Telefonbuch>
areacode:<Optional: your own area code; will shorten the display of local numbers>

[ftp]
user: <User who can access the NAS directories of your FRITZ!Box via ftp, default: ftpuser>
password: <Password>

[webcam]
title: <Optional: title of the webcam snapshots to be displayed>
url: <URL for the webcam snapshot, e.g.. http://1.1.1.1/snapshot>
user: <webcam user>
password: <webcam password>
width: <For 8851: 559; configure according to model and preference>
height: <For 8851: 265; configure according to model and preference>


Phone setup:
============
Enter http://<Phone IP address>/admin/advanced in the address filed of your bowser (login as user "admin" if required) -> Voice -> Phone
Confgure the following settings in section XML Service (names can be adapted according to your preference):
XML Directory Service Name:	FRITZ!Box Phonebook
XML Directory Service URL:	http://<web server ip address>/cgi-bin/fb_phonebook.cgi
XML Application Service Name:	FRITZ!Box Services
XML Application Service URL:	http://<web server ip address>/cgi-bin/fb_services.cgi
