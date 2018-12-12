import requests
import argparse
import urllib.parse
import os
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup 

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--silent", help="Run without extra messages", action="store_true")
parser.add_argument("-d", "--days", help="How many days to go back (1= today)", type=int, default=1)
parser.add_argument("-c", "--country", help="Which Country, default UK, other options (UK|US|CA|JP|ALL)", type=str, default="ALL")

plexURL = "http://192.168.1.114:32400"
plexToken = ""
OMDBAPI = ""
theMovieDBAPI = ""
ignorefilename = 'ignorefilms.txt'
grabfilename = 'grabfilms'

args = parser.parse_args()

days = args.days
country = args.country

UKUrlPart = "en_GB"
USUrlPart = "en_US"
CAUrlPart = "en_CA"
JPUrlPart = "ja_JP"

if country=="UK" :
	CountryUrlPart = UKUrlPart

if country=="US" :
	CountryUrlPart = USUrlPart
	
if country=="CA" :
	CountryUrlPart = CAUrlPart	
	
if country=="JP" :
	CountryUrlPart = JPUrlPart	

#Scan new on Netflix for films which aren't in our library
#Add option to ignore films
#Create file with those to download and from where

res = requests.get(plexURL+"/library/sections/1/all?type=1&includeCollections=0&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en&X-Plex-Text-Format=plain")
#print(plexURL+"/library/sections/1/all?type=1&includeCollections=0&X-Plex-Product=Plex%20Web&X-Plex-Version=3.67.1&X-Plex-Platform=Firefox&X-Plex-Platform-Version=61.0&X-Plex-Sync-Version=2&X-Plex-Device=Windows&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1920x929%2C1920x1080&X-Plex-Token="+plexToken+"&X-Plex-Language=en&X-Plex-Text-Format=plain")
#exit()
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

def IMDBInfo(title,year):
	res= requests.get("http://www.omdbapi.com/?apikey="+OMDBAPI+"&type=movie&r=xml&t="+title+"&y="+str(year))
	IMDBResponse = BeautifulSoup(res.text,"html.parser")
	IMDBMovie = IMDBResponse.select_one('movie')
	IMDBRating = ""
	#metaRating = ""
	if IMDBMovie:
		IMDBRating = str(IMDBMovie.get("imdbrating")) + "/10 "
		IMDBUrl = "https://www.imdb.com/title/" + str(IMDBMovie.get("imdbid"))
		#metaRating = "MetaCritic : "+str(IMDBMovie.get("metascore"))
		return " "+title+" ("+str(year)+") "+IMDBRating+"\n  "+IMDBUrl
	else:
		return " "+title+" ("+str(year)+")\n  (No Matches on IMDB)"
	
def ignoredFilms(title,year,locale):
	filmString = title + " ("+str(year)+")"
	if os.path.isfile(ignorefilename) and filmString in open(ignorefilename).read():
		if not args.silent:
			print(title +" is in Ignore list")
		return True
	elif os.path.isfile(grabfilename+'_'+locale+'.txt') and filmString in open(grabfilename+'_'+locale+'.txt').read():
		if not args.silent:
			print(title +" is already in Grab list")
			return True
		else:
			return False
	else:
		return False
		
def checkFilm(title,year):
	if "," in title:
		print(" "+title+" : Skipped due to name")
		return
	matchMovie = LibraryMovies.select_one('video[title="'+title+'"]')
	if matchMovie and matchMovie.get("year") == str(year):
		if not args.silent:
			print(title +" is already in our Films Library")	
		return False
	else:
		matchKidsMovie = LibraryKidsMovies.select_one('video[title="'+title+'"]')
		if matchKidsMovie and matchKidsMovie.get("year") == str(year):
			if not args.silent:
				print(title +" is already in Kids Films")
			return False
		else:
			print(IMDBInfo(title,year))
			return True
		print("")

#print(soup)

def lookupURL(movieID,locale):
	res = requests.get('https://apis.justwatch.com/content/titles/movie/'+str(movieID)+'/locale/'+locale)
	try:
		FilmJSON = res.json()
		offers = FilmJSON['offers']
		for offer in offers:
			if offer['provider_id'] == 8:
				return offer['urls']['standard_web']
				break
	except:
		return None

def checkNewOnNetflix(CountryCode):
	NetflixURL = "https://apis.justwatch.com/content/titles/"+CountryCode+"/new?body=%7B%22age_certifications%22:null,%22content_types%22:%5B%22movie%22%5D,%22genres%22:null,%22languages%22:null,%22max_price%22:null,%22min_price%22:null,%22monetization_types%22:%5B%22flatrate%22,%22ads%22,%22free%22,%22rent%22,%22buy%22%5D,%22page%22:"+str(days)+",%22page_size%22:200,%22presentation_types%22:null,%22providers%22:%5B%22nfx%22%5D,%22release_year_from%22:null,%22release_year_until%22:null,%22scoring_filter_types%22:null,%22timeline_type%22:null,%22titles_per_provider%22:200%7D"
	res = requests.get(NetflixURL)
	NetflixMovies = res.json()
	#print(NetflixURL)
	NetFlixItems = NetflixMovies['days'][0]['providers']

	if not args.silent:
		print("")
		print("Getting full list of new Netflix Movies in " + CountryCode[3:])


	for movie in NetFlixItems[0]['items']:
		try:
			asciiname = movie['title'].encode('ascii')
		except:
			print("Skipped Non ascii-encoded unicode string")
		else:
			if not ignoredFilms(movie['title'],movie['original_release_year'],CountryCode[3:]):
				if checkFilm(movie['title'],movie['original_release_year']):
					#print(movie)
					print("  Netflix Region : "+ CountryCode[3:])
					setRecording = input("Should we download this Film? (y|n) ")
					if setRecording.lower() == "y":
						# Add to the Grab list
						with open(grabfilename+'_'+CountryCode[3:]+'.txt', 'a') as file:
							file.write(movie['title'] + " ("+str(movie['original_release_year'])+")\n")
							file.write(lookupURL(movie['id'],CountryCode)+"\n")
							file.close			
					if setRecording.lower() == "n":
						# Add to the ignore list
						with open(ignorefilename, 'a') as file:
							file.write(movie['title'] + " ("+str(movie['original_release_year'])+") ("+CountryCode[3:]+")\n")
							file.close

if country=="ALL":
	checkNewOnNetflix(UKUrlPart)
	checkNewOnNetflix(USUrlPart)
	checkNewOnNetflix(CAUrlPart)
	checkNewOnNetflix(JPUrlPart)
else:
	checkNewOnNetflix(CountryUrlPart)

