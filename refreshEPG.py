#!/usr/bin/python3

import requests

plexToken = ""
DVRID = "16"

refreshEPG = "http://192.168.1.114:32400/livetv/dvrs/"+DVRID+"/reloadGuide?X-Plex-Token=" +plexToken

res = requests.post(refreshEPG)
if res.status_code == 200:
	print(" Refreshing EPG")
else:
	print(" Error Returned : "+str(res.status_code))
