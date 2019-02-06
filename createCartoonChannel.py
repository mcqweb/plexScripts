#!/usr/bin/python3
# pip install plexapi
from plexapi.server import PlexServer
import random
import requests

### Edit Settings ###
PLEX_URL = ''
TOKEN = ''

LIBRARY = 'Kids TV Shows'
PLAYLIST_TITLE = 'Cartoon Channel'
TOTAL_EPISODES = 2 # Number of Episodes from each show to add to playlist
SHOWS = ['Tom and Jerry','The Tom and Jerry Show (2014)','Be Cool, Scooby-Doo!','New Looney Tunes']
###/ Edit Settings ###

plex = PlexServer(PLEX_URL, TOKEN)



account = plex.myPlexAccount()
user = account.user('') # If using a managed user, otherwise just set user_plex = plex
play_lst= []
print(user.title)
user_plex = PlexServer(PLEX_URL, user.get_token(plex.machineIdentifier))

for show in user_plex.library.section(LIBRARY).all():
	if show.title in SHOWS:
		episode_lst = []
		for episode in show.unwatched():
			episode_lst += [episode]
		temp_lst = random.sample(episode_lst, TOTAL_EPISODES)
		play_lst = list(set(play_lst + temp_lst))

#REMOVE EXISTING PLAYLIST
for playlist in user_plex.playlists():
	if playlist.title == PLAYLIST_TITLE:
		print('Removing old Playlist')
		playlist.delete()			
user_plex.createPlaylist(PLAYLIST_TITLE, play_lst)
