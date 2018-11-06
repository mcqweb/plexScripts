# TODO
# Check the libraries to ensure we haven't already recorded this episode/film, although perhaps Plex will take care of that itself?
# Use a SQLITE3 db to store these keywords so you can schedule a run to create recordings
# Use an OMDB lookup to better check for actors or use the plex details feed, the movies EPG XML only contains a subset

# Usage 
# To Preview matches : python keywordPVR.py "Search Phrase" 
# To Auto Record matches : python keywordPVR.py "Search Phrase" -r`

import requests
import argparse
import urllib.parse
import os
from bs4 import BeautifulSoup 

parser = argparse.ArgumentParser()
parser.add_argument("search", help="Enter the search term to look for")
parser.add_argument("-r","--record", help="Create a Recording for each match", action="store_true")
args = parser.parse_args()



#Set some default values
plexURL = ""
plexToken = ""
schedulingDefaults = "/media/subscriptions?prefs%5BminVideoQuality%5D=0&prefs%5BreplaceLowerQuality%5D=false&prefs%5BrecordPartials%5D=true&prefs%5BstartOffsetMinutes%5D=3&prefs%5BendOffsetMinutes%5D=5&prefs%5BlineupChannel%5D=&prefs%5BstartTimeslot%5D=-1&prefs%5BcomskipEnabled%5D=-1&prefs%5BoneShot%5D=true&targetSectionLocationID=&includeGrabs=1&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Chrome&X-Plex-Platform-Version=69.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Chrome&X-Plex-Device-Screen-Resolution=1920x969%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en-GB"

# Target Record Directories and DVR Service
movieTargetLibraryID = "15"
TVTargetLibraryID = "16"
SportTargetLibraryID = "16"
mediaProviderID = "17"
epgID = "16"

keyword = args.search

#Get a list of all scheduled recordings
res = requests.get(plexURL+"/media/subscriptions?X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en")
ScheduledRecordings = BeautifulSoup(res.text,"html.parser")

def checkSchedule(guid):
	#check to see if this episode or film is already scheduled.
	matchItem = ScheduledRecordings.select_one('video[guid="'+guid+'"]')
	if matchItem:
		return True
	else:
		return False
		
def recordEpisode(Episode,isSport):
	#Create the recording
	RecordURL = plexURL+schedulingDefaults	
	if isSport:
		RecordURL += "&targetLibrarySectionID="+SportTargetLibraryID
	else:
		RecordURL += "&targetLibrarySectionID="+TVTargetLibraryID
	if Episode.has_attr("grandparentguid"):
		RecordURL += "&hints[grandparentGuid]="+urllib.parse.quote_plus(Episode['grandparentguid'])
	if Episode.has_attr("grandparentthumb"):
		RecordURL += "&hints[grandparentThumb]="+urllib.parse.quote_plus(Episode['grandparentthumb'])
	if Episode.has_attr("grandparenttitle"):
		RecordURL += "&hints[grandparentTitle]="+urllib.parse.quote_plus(Episode['grandparenttitle'])
	if Episode.has_attr("grandparentyear"):
		RecordURL += "&hints[grandparentYear]="+urllib.parse.quote_plus(Episode['grandparentyear'])
	if Episode.has_attr("guid"):
		RecordURL += "&hints[guid]="+urllib.parse.quote_plus(Episode['guid'])
	if Episode.has_attr("index"):
		RecordURL += "&hints[index]="+urllib.parse.quote_plus(Episode['index'])
	if Episode.has_attr("originallyavailableat"):
		RecordURL += "&hints[originallyAvailableAt]="+urllib.parse.quote_plus(Episode['originallyavailableat'])
	if Episode.has_attr("parentindex"):
		RecordURL += "&hints[parentIndex]="+urllib.parse.quote_plus(Episode['parentindex'])
	if Episode.has_attr("title"):
		RecordURL += "&hints[title]="+urllib.parse.quote_plus(Episode['title'])
	if Episode.has_attr("type"):
		RecordURL += "&hints[type]="+urllib.parse.quote_plus(Episode['type'])
	if Episode.has_attr("year"):
		RecordURL += "&hints[year]="+urllib.parse.quote_plus(Episode['year'])
	if Episode.has_attr("airingchannels"):
		RecordURL += "&params[airingChannels]="+urllib.parse.quote_plus(Episode['airingchannels'])
	RecordURL += "&params[libraryType]=2&type=4&params[mediaProviderID]="+mediaProviderID
	
	if args.record:
		res = requests.post(RecordURL)
		if res.status_code == 200:
			print(" Recording successfully created")
			return True
		else:
			print(" Error Returned : "+res.status_code)
			return False
	
def recordMovie(Movie):
	# Create the recording
	RecordURL = plexURL+schedulingDefaults
	if Movie.has_attr("guid"):
		RecordURL+="&hints[guid]="+urllib.parse.quote_plus(Movie['guid'])
	if Movie.has_attr("title"):
		RecordURL+="&hints[title]="+urllib.parse.quote_plus(Movie['title'])
	if Movie.has_attr("year"):
		RecordURL+="&hints[year]="+Movie['year']
	if Movie.has_attr("thumb"):
		RecordURL+="&hints[thumb]="+urllib.parse.quote_plus(Movie['thumb'])
	RecordURL += "&hints[type]=1&params[libraryType]=1&type=1&params[mediaProviderID]="+mediaProviderID+"&targetLibrarySectionID="+movieTargetLibraryID
	if args.record:
		res = requests.post(RecordURL)
		if res.status_code == 200:
			print(" Recording successfully created")
			return True
			#print(RecordURL)
		else:
			print(" Error Returned : "+res.status_code)
			return False

#
getEpisodeInfo = plexURL+"/tv.plex.providers.epg.onconnect:"+epgID+"/sections/2/all?type=4&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=62.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x966%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en&X-Plex-Text-Format=plain"

res = requests.get(getEpisodeInfo)

EPGEpisodes = BeautifulSoup(res.text,"html.parser")

print("")
print("Searching for Episodes containing the keyword(s) : "+keyword.lower())
for Episode in EPGEpisodes.find_all("video"):
	#Check for our keyword
	if keyword.lower() in Episode['summary'].lower():
		print(" (" + Episode['grandparenttitle'] + ")" + Episode['title'] + " : Episode Summary Match")
		if checkSchedule(Episode['guid']):
			print(" Already Scheduled")
		else:
			recordEpisode(Episode,False)		
	if keyword.lower() in Episode['title'].lower():
		print(" (" + Episode['grandparenttitle'] + ") " + Episode['title'] + " : Episode Title Match")
		if checkSchedule(Episode['guid']):
			print(" Already Scheduled")
		else:
			recordEpisode(Episode,False)			
	

getSportsInfo = plexURL+"/tv.plex.providers.epg.onconnect:"+epgID+"/sections/3/all?type=4&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=62.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x966%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en&X-Plex-Text-Format=plain"

res = requests.get(getSportsInfo)

EPGSports = BeautifulSoup(res.text,"html.parser")	

print("")
print("Searching for Sports Airings containing the keyword(s) : "+keyword.lower())
for Episode in EPGSports.find_all("video"):
	#Check for our keyword
	if keyword.lower() in Episode['summary'].lower():
		print(" ("+Episode['grandparenttitle'] + ") " + Episode['title'] + " : Sports Summary Match")
		if checkSchedule(Episode['guid']):
			print(" Already Scheduled")
		else:
			recordEpisode(Episode,True)
	if keyword.lower() in Episode['title'].lower():
		print(" ("+Episode['grandparenttitle'] + ") " + Episode['title'] + " : Sports Title Match")
		if checkSchedule(Episode['guid']):
			print(" Already Scheduled")
		else:
			recordEpisode(Episode,True)			
		
		
getMovieInfo = plexURL+"/tv.plex.providers.epg.onconnect:"+epgID+"/sections/1/all?type=1&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=62.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x966%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en&X-Plex-Text-Format=plain"

res = requests.get(getMovieInfo)

Movies = BeautifulSoup(res.text,"html.parser")	

print("")
print("Searching for Films containing the keyword(s) or participants : "+keyword.lower())
for Movie in Movies.find_all("video"):
	#Check for our keyword
	if keyword.lower() in Movie['summary'].lower():
		print(" "+Movie['title'] + " : Movie Summary Match")
		if checkSchedule(Movie['guid']):
			print("Already Scheduled")
		else:
			recordMovie(Movie)
	if keyword.lower() in Movie['title'].lower():
		print(" " + Movie['title'] + " : Movie Title Match")
		if checkSchedule(Movie['guid']):
			print("Already Scheduled")
		else:
			recordMovie(Movie)
	for child in Movie.find_all(["director","writer","role"]):
		if keyword.lower() in child['tag'].lower():
			print(" " + Movie['title'] + " : Movie Person Match")
			if checkSchedule(Movie['guid']):
				print("Already Scheduled")
			else:
				recordMovie(Movie)
		
