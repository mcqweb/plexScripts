import requests
import argparse
import urllib.parse
import os
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup 

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--silent", help="Run without extra messages", action="store_true")

plexURL = "http://192.168.1.114:32400"
plexToken = ""
OMDBAPI = ""
ignorefilename = 'ignorefilms.txt'

args = parser.parse_args()

res = requests.get(plexURL+"/tv.plex.providers.epg.onconnect:16/sections/1/all?type=1&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en&X-Plex-Text-Format=plain")

if not args.silent:
	print("")
	print("Checking for Movies in EPG")
EPGMovies = BeautifulSoup(res.text,"html.parser")

if not args.silent:
	print(str(len(EPGMovies.find_all('video')))+" movie(s) found")

res = requests.get(plexURL+"/library/sections/1/all?type=1&includeCollections=0&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en&X-Plex-Text-Format=plain")


if not args.silent:
	print("")
	print("Getting full list of movies in our main library")
LibraryMovies = BeautifulSoup(res.text,"html.parser")

if not args.silent:
	print(str(len(LibraryMovies.find_all('video')))+" movie(s) found")

res = requests.get(plexURL+"/library/sections/2/all?type=1&includeCollections=0&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en&X-Plex-Text-Format=plain")


if not args.silent:
	print("")
	print("Getting full list of movies in our Kids library")
LibraryKidsMovies = BeautifulSoup(res.text,"html.parser")

if not args.silent:
	print(str(len(LibraryKidsMovies.find_all('video')))+" movie(s) found")

	print("")
	print("Checking for previously scheduled recordings")
res = requests.get(plexURL+"/media/subscriptions?X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en")

ScheduledRecordings = BeautifulSoup(res.text,"html.parser")

if not args.silent:
	print(str(len(ScheduledRecordings.find_all('video', {'type' : 'movie'})))+" movie(s) found")
	print("")

print("Here is a full list of missing movies with (currently) no scheduled Recordings")
print("")

def ignoredFilms(title,year):
	filmString = title + " ("+year+")"
	if os.path.isfile(ignorefilename) and filmString in open(ignorefilename).read():
		if not args.silent:
			print(title +" is in Ignore list")
		return True
	else:
		return False

def checkSchedule(title,year):
	matchMovie = ScheduledRecordings.select_one('video[title="'+title+'"]')
	if matchMovie and matchMovie.get("year") == year:
		return True
	else:
		return False

def IMDBInfo(title,year):
	res= requests.get("http://www.omdbapi.com/?apikey="+OMDBAPI+"&type=movie&r=xml&t="+title+"&y="+year)
	IMDBResponse = BeautifulSoup(res.text,"html.parser")
	IMDBMovie = IMDBResponse.select_one('movie')
	IMDBRating = ""
	#metaRating = ""
	if IMDBMovie:
		IMDBRating = str(IMDBMovie.get("imdbrating")) + "/10 "
		IMDBUrl = "https://www.imdb.com/title/" + str(IMDBMovie.get("imdbid"))
		#metaRating = "MetaCritic : "+str(IMDBMovie.get("metascore"))
		return " "+title+" ("+year+") "+IMDBRating+"\n  "+IMDBUrl
	else:
		return " "+title+" ("+year+")\n  (No Matches on IMDB)"
	
	
		
def checkFilm(title,year):
	if "," in title:
		print(" "+title+" : Skipped due to name")
		return
	matchMovie = LibraryMovies.select_one('video[title="'+title+'"]')
	if matchMovie and matchMovie.get("year") == year:
		if not args.silent:
			print(title +" is already in our Films Library")	
		return False
	else:
		matchKidsMovie = LibraryKidsMovies.select_one('video[title="'+title+'"]')
		if matchKidsMovie and matchKidsMovie.get("year") == year:
			if not args.silent:
				print(title +" is already in Kids Films")
			return False
		else:
			#We need to check if there is already a subscription for this film
			if checkSchedule(title,year):
				if not args.silent:
					print(title + " is scheduled to record")
				return
			else:
				print(IMDBInfo(title,year))
				return True
			print("")
#print(soup)
for movie in EPGMovies.find_all("video"):
	#Check our Ignore list
	if not ignoredFilms(movie['title'],movie['year']):
		if checkFilm(movie['title'],movie['year']):
			setRecording = input("Should we set a recording for this Film? (y|i|n) ")
			if setRecording.lower() == "y":
				hintGuid="&hints[guid]="+urllib.parse.quote_plus(movie['guid'])+"&"
				hintTitle="hints[title]="+urllib.parse.quote_plus(movie['title'])+"&"
				hintYear="hints[year]="+movie['year']+"&"
				hintThumb="hints[thumb]="+urllib.parse.quote_plus(movie['thumb'])+"&"
				RecordURL = plexURL+"/media/subscriptions?prefs%5BminVideoQuality%5D=0&prefs%5BreplaceLowerQuality%5D=false&prefs%5BrecordPartials%5D=true&prefs%5BstartOffsetMinutes%5D=3&prefs%5BendOffsetMinutes%5D=5&prefs%5BlineupChannel%5D=&prefs%5BstartTimeslot%5D=-1&prefs%5BcomskipEnabled%5D=-1&prefs%5BoneShot%5D=true&targetLibrarySectionID=15&targetSectionLocationID=&includeGrabs=1"+hintGuid+hintThumb+hintTitle+hintYear+"hints[type]=1&params[libraryType]=1&params[mediaProviderID]=17&type=1&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en"
				res = requests.post(RecordURL)
				if res.status_code == 200:
					print("Recording successfully added")
					#print(RecordURL)
				else:
					print("Error Returned : "+res.status_code)
			if setRecording.lower() == "i":
				# Add to the ignore list
				with open(ignorefilename, 'a') as file:
					file.write(movie['title'] + " ("+movie['year']+")\n")
					file.close
		
	


