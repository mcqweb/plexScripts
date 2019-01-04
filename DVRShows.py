import requests
import argparse
import urllib.parse
import os
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup 
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--silent", help="Run without extra messages", action="store_true")
parser.add_argument("-p", "--premiere", help="Only prompt for Premiere's", action="store_true")
parser.add_argument("-n", "--new", help="Only prompt episodes added in last 24 hours", action="store_true")

plexURL = "http://192.168.1.114:32400"
plexToken = ""
OMDBAPI = ""
ignorefilename = 'ignoreshows.txt'
if os.path.isfile(networkpath+ignorefilename):
	ignorelist = open(networkpath+ignorefilename).read()
	
TVURL = plexURL+"/tv.plex.providers.epg.onconnect:16/sections/2/all?type=4&X-Plex-Container-Start=0&X-Plex-Container-Size=5000&X-Plex-Product=Plex%20Web&X-Plex-Version=3.77.4&X-Plex-Platform=Chrome&X-Plex-Platform-Version=70.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Chrome&X-Plex-Device-Screen-Resolution=1920x969%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en-GB&X-Plex-Text-Format=plain"
schedulingDefaults = "/media/subscriptions?prefs%5BminVideoQuality%5D=0&prefs%5BreplaceLowerQuality%5D=false&prefs%5BrecordPartials%5D=true&prefs%5BstartOffsetMinutes%5D=3&prefs%5BendOffsetMinutes%5D=5&prefs%5BlineupChannel%5D=&prefs%5BstartTimeslot%5D=-1&prefs%5BcomskipEnabled%5D=-1&prefs%5BoneShot%5D=true&targetSectionLocationID=&includeGrabs=1&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Client-Identifier=kud0vo2yuks7385vlmhgm8lv&X-Plex-Platform=Chrome&X-Plex-Platform-Version=69.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Chrome&X-Plex-Device-Screen-Resolution=1920x969%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en-GB"
today = datetime.today()
yesterday = today - timedelta(1) 
TVTargetLibraryID = "16"
mediaProviderID = "17"
epgID = "16"

def ignoredShows(showtitle,episodetitle):
	if showtitle+"\n" in ignorelist:
		if not args.silent:
			print(showtitle +" is in Ignore list")
		return True
	if episodetitle in ignorelist:
		if not args.silent:
			print(episodetitle +" is in Ignore list")
		return True
	else:
		return False

def checkSchedule(showtitle,episodetitle):
	matchShow = ScheduledRecordings.select_one('directory[title="'+episodetitle.replace(','," ")+'"]')
	if matchShow: 
		print("We're already recording all episodes of "+episodetitle)
		return True
	else:
		try:
			matchEpisode = ScheduledRecordings.select_one('video[grandparenttitle="'+episodetitle.replace(','," ")+'"]')
			if matchEpisode: 
				print("We're already recording this episode of "+episodetitle)
				return True
			else:
				return False
		except:
			return False

def recordEpisode(Episode,fullShow):
	#Create the recording
	RecordURL = plexURL+schedulingDefaults	
	RecordURL += "&targetLibrarySectionID="+TVTargetLibraryID
	if fullShow:
		RecordURL += "&prefs%5BonlyNewAirings%5D=1"
	if Episode.has_attr("grandparentguid"):
		if fullShow:
			RecordURL += "&hints[guid]="+urllib.parse.quote_plus(Episode['grandparentguid'])
		else:
			RecordURL += "&hints[grandparentGuid]="+urllib.parse.quote_plus(Episode['grandparentguid'])
	if Episode.has_attr("grandparentthumb"):
		if fullShow:
			RecordURL += "&hints[thumb]="+urllib.parse.quote_plus(Episode['grandparentthumb'])
		else:
			RecordURL += "&hints[grandparentThumb]="+urllib.parse.quote_plus(Episode['grandparentthumb'])
	if Episode.has_attr("grandparenttitle"):
		if fullShow:
			RecordURL += "&hints[title]="+urllib.parse.quote_plus(Episode['grandparenttitle'])
		else:
			RecordURL += "&hints[grandparentTitle]="+urllib.parse.quote_plus(Episode['grandparenttitle'])
	if Episode.has_attr("grandparentyear"):
		if fullShow:
			RecordURL += "&hints[year]="+urllib.parse.quote_plus(Episode['grandparentyear'])
		else:
			RecordURL += "&hints[grandparentYear]="+urllib.parse.quote_plus(Episode['grandparentyear'])
	if not fullShow and Episode.has_attr("guid"):
		RecordURL += "&hints[guid]="+urllib.parse.quote_plus(Episode['guid'])
	if not fullShow and Episode.has_attr("index"):
		RecordURL += "&hints[index]="+urllib.parse.quote_plus(Episode['index'])
	if not fullShow and Episode.has_attr("originallyavailableat"):
		RecordURL += "&hints[originallyAvailableAt]="+urllib.parse.quote_plus(Episode['originallyavailableat'])
	if not fullShow and Episode.has_attr("parentindex"):
		RecordURL += "&hints[parentIndex]="+urllib.parse.quote_plus(Episode['parentindex'])
	if not fullShow and Episode.has_attr("title"):
		RecordURL += "&hints[title]="+urllib.parse.quote_plus(Episode['title'])
	if Episode.has_attr("type"):
		if fullShow:
			RecordURL += "&hints[type]=2&type=2"
		else:
			RecordURL += "&hints[type]=4&type=4"
	if not fullShow and Episode.has_attr("year"):
		RecordURL += "&hints[year]="+urllib.parse.quote_plus(Episode['year'])
	if Episode.has_attr("airingchannels"):
		RecordURL += "&params[airingChannels]="+urllib.parse.quote_plus(Episode['airingchannels'])
	RecordURL += "&params[libraryType]=2&params[mediaProviderID]="+mediaProviderID
	
	res = requests.post(RecordURL)
	if res.status_code == 200:
		print(" Recording successfully created")
		return True
	else:
		print(" Error Returned : "+res.status_code)
		return False

args = parser.parse_args()
res = requests.get(TVURL)

if not args.silent:
	print("")
	print("Checking for New Shows in EPG")
EPGShows = BeautifulSoup(res.text,"html.parser")

if not args.silent:
	print("")
	print("Checking for previously scheduled recordings")
res = requests.get(plexURL+"/media/subscriptions?X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en")

ScheduledRecordings = BeautifulSoup(res.text,"html.parser")

if not args.silent:
	print(str(len(ScheduledRecordings.find_all('directory', {'type' : 'show'})))+" show(s) found")
	print("")

print("Here is a full list of missing shows with (currently) no scheduled Recordings")
if args.premiere:
	print("We're only looking for first airings")
if args.new:
	print("We're only looking for episodes added recently")	
print("")


#print(soup)
for Episode in EPGShows.find_all("video"):
	firstAired = Episode['originallyavailableat']
	dateAdded = datetime.utcfromtimestamp(int(Episode['addedat']))
	premiere = True
	new = True
	if args.premiere:
		#We need to check the First Aired Date
		for airing in Episode.find_all("media"):
			try:
				premiere=airing['premiere']
				premiere = True
			except:
				premiere = False
	if args.new:
		#We only want episodes added in the last 24 hours
		if dateAdded > yesterday:
			new = True
		else:
			new = False
	if premiere and new and not ignoredShows(Episode['grandparenttitle'], Episode['grandparenttitle']+" ("+Episode['parenttitle']+") - "+Episode['title']):
		if not checkSchedule(Episode['title'],Episode['grandparenttitle']):
			print(Episode['grandparenttitle']+" ("+Episode['parenttitle']+") - "+Episode['title'])
			setRecording = input("Should we set a recording for this Show? (y|e|i|n|m|s) ")
			if setRecording.lower() == "m":
				print("\nMore Info Requested...")
				print(" Added to EPG on : " + dateAdded.strftime('%Y-%m-%d'))
				print(" First aired on : " + firstAired[:10])
				print(" "+Episode['summary'])
				setRecording = input("\nShould we set a recording for this Show? (y|e|i|n|s) ")
			if setRecording.lower() == "s":
				# Add to the ignore list
				with open(ignorefilename, 'a') as file:
					ignorelist += Episode['grandparenttitle']+'\n'
					file.write(Episode['grandparenttitle']+'\n')
					file.close
			if setRecording.lower() == "i":
				# Add to the ignore list
				with open(ignorefilename, 'a') as file:
					ignorelist += Episode['grandparenttitle']+'\n'
					file.write(Episode['grandparenttitle']+" ("+Episode['parenttitle']+") - "+Episode['title']+'\n')
					file.close
			if setRecording.lower() == "e":
				#We'll record just this episode
				recordEpisode(Episode,False)
			if setRecording.lower() == "y":
				#We'll record the full show going forwards
				recordEpisode(Episode,True)	
		
	


