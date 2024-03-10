from datetime import datetime
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import dotenv
import os

dotenv.load_dotenv()
redirect_uri = os.environ.get("SPOTIPY_REDIRECT_URI")
client_id = os.environ.get("SPOTIPY_CLIENT_ID")
client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
username = os.environ.get("username")

user_input = input("To what date you want to travel to?YYYY-MM-DD  ")

dt = datetime.strptime(user_input, "%Y%m%d")
year = dt.year
date = dt.strftime("%Y-%m-%d")

URL = f"https://www.billboard.com/charts/hot-100/{date}/"

# Write your code below this line 👇

res = requests.get(URL)
soup = BeautifulSoup(res.content, "html.parser")

headings = [song.h3 for song in soup.find_all(name="li", class_="lrv-u-width-100p")]
# print(headings)
songs = []
for elt in headings:
    try:
        title = elt.getText()
    except AttributeError:
        title = None
    else:
        song_title = title.split("\t")[9]
        songs.append(song_title)

# print(songs)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
    scope="playlist-modify-private",
    redirect_uri=redirect_uri,
    client_id=client_id,
    client_secret=client_secret,
    show_dialog=True,
    cache_path="token.txt",
    username=username, 
    )
    )
user_id = sp.current_user()["id"]

song_uris = []
for i in songs:
    try:
        song_info = sp.search(q=f"track:{i} year:{year}", type="track")
        song_uris.append(song_info["tracks"]["items"][0]["uri"])
    except IndexError:
        print(f"{i} does not exist.")


playlist_name = f"{date} top 100!"
playlist_id = sp.user_playlist_create(user_id, playlist_name, public=False, collaborative=False, description=f"{date} top 100 songs! from Billboard scraping!")

sp.user_playlist_add_tracks(user_id, playlist_id["id"], song_uris, position=None)
