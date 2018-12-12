#!/usr/bin/python3
import requests
import json 
import time
from plexapi.server import PlexServer
from lxml import html

PLEX_URL = ""
PLEX_TOKEN = ""
MOVIE_LIBRARY_NAME = "Films"
KIDSMOVIE_LIBRARY_NAME = "Kids Films"
OMDBAPI = ""
TMDB_API_KEY = ""
PLAYLIST_NAME = 'Christmas Films'
TMDB_REQUEST_COUNT = 0
playlist_items = []
KEYWORDS = ['xmas','christmas','santa']

def get_tmdb_id_from_imdb(imdb_id):
    global TMDB_REQUEST_COUNT
    #print("Looking up TMDB ID for :"+imdb_id)
    if not TMDB_API_KEY:
        return None
    
    # Wait 10 seconds for the TMDb rate limit
    if TMDB_REQUEST_COUNT >= 40:
        print("Rate limiting, waiting 10 seconds")
        time.sleep(10)
        TMDB_REQUEST_COUNT = 0
          
    params = {"api_key": TMDB_API_KEY, "external_source":"imdb_id"}
    
    
    url = "https://api.themoviedb.org/3/find/"+imdb_id
    r = requests.get(url, params=params)
    
    TMDB_REQUEST_COUNT += 1
    
    if r.status_code == 200:
        try:
            movie = json.loads(r.text)
            results = movie['movie_results'][0]
            return results['id']
        except:
            return None
    else:
        return None

def checkXmas(tmdb_id):
    try:
        tmdb_id = int(tmdb_id)
    except:
        tmdb_id = 0
        
    if tmdb_id > 0:
        #print("Checking : "+str(tmdb_id))
        res = requests.get("https://api.themoviedb.org/3/movie/"+str(tmdb_id)+"/keywords?api_key="+TMDB_API_KEY+"&language=en-US")
        movie = res.json()
        try:
            for keyword in movie['keywords']:
                #print(keyword['name'])
                if any(matchingkeyword in keyword['name'] for matchingkeyword in KEYWORDS):
                    return True
        except:
            print("No Keywords found")
        return False
    return False
        
try:
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
except:
    print("No Plex server found at: {base_url}".format(base_url=PLEX_URL))
    print("Exiting script.")

print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=MOVIE_LIBRARY_NAME))
try:
    movie_library = plex.library.section(MOVIE_LIBRARY_NAME)
    movie_library_key = movie_library.key
    library_language = movie_library.language
    movies = movie_library.all()
except:
    print("The '{library}' library does not exist in Plex.".format(library=MOVIE_LIBRARY_NAME))
   
#REMOVE THIS IF YOU ONLY HAVE 1 FILM LIBRARY
print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=KIDSMOVIE_LIBRARY_NAME))
try:
    movie_library = plex.library.section(KIDSMOVIE_LIBRARY_NAME)
    movie_library_key = movie_library.key
    library_language = movie_library.language
    kids_movies = movie_library.all()
except:
    print("The '{library}' library does not exist in Plex.".format(library=KIDSMOVIE_LIBRARY_NAME)) 

for m in movies:
    imdb_id = "0"
    tmdb_id = "0"

    if 'imdb://' in m.guid:
        imdb_id = m.guid.split('imdb://')[1].split('?')[0]
        tmdb_id = get_tmdb_id_from_imdb(imdb_id)
    elif 'themoviedb://' in m.guid:
        tmdb_id = m.guid.split('themoviedb://')[1].split('?')[0] 
    try:
        print(" Checking : " + m.title)
    except:
        print(" Non Ascii in title")
    if checkXmas(tmdb_id):
        print("CHRISTMAS FILM FOUND!!")
        playlist_items += [m]
    
for m in kids_movies:
    imdb_id = "0"
    tmdb_id = "0"

    if 'imdb://' in m.guid:
        imdb_id = m.guid.split('imdb://')[1].split('?')[0]
        tmdb_id = get_tmdb_id_from_imdb(imdb_id)
    elif 'themoviedb://' in m.guid:
        tmdb_id = m.guid.split('themoviedb://')[1].split('?')[0] 
    try:
        print(" Checking : " + m.title)
    except:
        print(" Non Ascii in title")
    if checkXmas(tmdb_id):
        print("MATCHING FILM FOUND!!")
        playlist_items += [m]
    
for playlist in plex.playlists():
    if playlist.title == PLAYLIST_NAME:
        print('Removing old Playlist')
        playlist.delete()

print('Creating New Playlist')
plex.createPlaylist(PLAYLIST_NAME, playlist_items)  
