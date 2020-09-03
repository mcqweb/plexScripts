#!/usr/bin/python3
# pip install plexapi
from plexapi.server import PlexServer
import random
import requests

### Edit Settings ###
PLEX_URL = ''
TOKEN = ''

LIBRARY = 'TV Shows'
PLAYLIST_TITLE = 'Unwatched Comedy'
TOTAL_EPISODES = 6 # Number of Episodes in total to add to playlist
SHOWS = ['The Detour (2016)','Difficult People','House of Lies',"Schitt's Creek",'Single Parents','Superstore','The Goldbergs (2013)', 'Brooklyn Nine-Nine','Cuckoo','The Good Place','What We Do In The Shadows','The Other Two']
###/ Edit Settings ###

plex = PlexServer(PLEX_URL, TOKEN)
play_lst= []


for show in plex.library.section(LIBRARY).all():
	if show.title in SHOWS:
		episode_lst = []
		for episode in show.unwatched():
			if episode.season().title=='Specials':
				continue
			if episode_lst == []:
				# We only want the first unwatched
				episode_lst += [episode]
			else:
				break					
		play_lst = list(set(play_lst + episode_lst))

#REMOVE EXISTING PLAYLIST
for playlist in plex.playlists():
	if playlist.title == PLAYLIST_TITLE:
		print('Removing old Playlist')
		playlist.delete()	
if len(play_lst) < TOTAL_EPISODES:
	TOTAL_EPISODES = len(play_lst)
plex.createPlaylist(PLAYLIST_TITLE, random.sample(play_lst, TOTAL_EPISODES))
