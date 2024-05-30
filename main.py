import requests
from bs4 import BeautifulSoup
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth

# Webscrape billboard top 100

billboard_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
billboard_website = f"https://www.billboard.com/charts/hot-100/{billboard_date}"

with requests.get(billboard_website) as billboard:
    soup = BeautifulSoup(billboard.text, "html.parser")
    top_song_list = soup.select(selector="li h3#title-of-a-story")
    top_song_artist_list = soup.select(selector="li span.a-no-trucate")
    top_song_info = [{"song": top_song_list[i].getText().strip(),
                      "artist": top_song_artist_list[i].get_text().strip().split()[0]}
                     for i in range(len(top_song_list))]

# Authentication with spotify

SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = os.environ["SPOTIPY_REDIRECT_URI"]
scope = "playlist-modify-private playlist-modify-public"

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope,
    cache_path=".cache"
)

sp = spotipy.Spotify(auth_manager=auth_manager)
user_id = sp.current_user()["id"]

# Pulling song uris

top_song_uri = []

for info in top_song_info:

    try:
        song_uri = sp.search(q=f"track:{info['song']} artist:{info['artist']}",
                             limit=1)["tracks"]["items"][0]["uri"]
    except IndexError:
        print(f"This song is not available on spotify: {info['song']}")
    else:
        top_song_uri.append(song_uri)

# Creating playlists

playlist_name = f"Personal Coding Project - Webscraped the Billboard Hot 100 for the date: {billboard_date}"
play_list_description = f"The Billboard Hot 100 for the date: {billboard_date}"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description= play_list_description)
playlist_id = playlist["id"]


sp.playlist_add_items(playlist_id=playlist_id, items=top_song_uri)
