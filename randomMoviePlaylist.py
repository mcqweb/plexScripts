# pip install plexapi
from plexapi.server import PlexServer
import random
import requests

### Edit Settings ###
PLEX_URL = ''
TOKEN = ''

LIBRARY = 'Films'
PLAYLIST_TITLE = 'Random Unwatched Movies'
TOTAL_FILMS = 20 # Number of Films to add to playlist
###/ Edit Settings ###

plex = PlexServer(PLEX_URL, TOKEN)

child_lst = []
aired_lst = []

# Remove Any Existing Random Playlists
for playlist in plex.playlists():
    if playlist.title == PLAYLIST_TITLE:
        print('Removing old Playlist ')
        playlist.delete()

# Get all unwatched movies from LIBRARY_NAME
for child in plex.library.section(LIBRARY).search(unwatched=True):
	child_lst += [child]

play_list = random.sample(child_lst, TOTAL_FILMS)
plex.createPlaylist(PLAYLIST_TITLE, play_list)
