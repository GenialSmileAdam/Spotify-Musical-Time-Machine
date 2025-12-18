from welcome import TITLE_TEXT
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# from pprint import pprint
import datetime as dt
import os
from dotenv import load_dotenv
import time as cronos

load_dotenv(".env")

now = dt.datetime.now().year
print(TITLE_TEXT)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) "
                        "Gecko/20100101 Firefox/131.0"}

def time_of_songs():
    year=int(input("what year would you like to travel back to?: "))
    if 2000<= year >=  now:
        raise ValueError(f"You entered a wrong year, try between 2000-{now}")

    month= int(input(f"What month would you like to travel to in {year}: "))
    if month >12:
        raise ValueError("Input is too High, try something a little lower")
    if month < 10:
        month = f"0{month}"

    day = int(input("what day exactly? : "))

    if day >= 30:
        raise  ValueError("Input is too High,try something a little lower")
    elif day < 10:
        day= f"0{day}"
    print("\nProgram is loading......")
    return year, month, day




def webscrape_billboard_charts(url):
    response = requests.get(url, headers=header)
    response.raise_for_status()
    file = response.text

    soup = BeautifulSoup(file, "html.parser")

    titles = soup.select("li li h3")

    songs = [title.getText().strip() for title in titles]


    return songs




def create_spotify_playlist(songs, time):
    no_of_songs = len(songs)
    scope = "playlist-modify-private playlist-read-private user-read-private"
    songs_list = []
    redirect_url = os.getenv("REDIRECT_URL")

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri= redirect_url,
        cache_path="token.txt",
        username="Jason Hughes",
        show_dialog=True
    ))
    # GETS USER ID!!!!
    # user_id = sp.current_user()["id"]
    # pprint(user_id)
    user_id = os.getenv("USER_ID")
    playlist = sp.user_playlist_create(user=user_id,
                                         name=f"Top 100 Songs of {time[0]}",
                                         public=False,
                                         description=f"Top 100 songs of {time[0]} gotten from "
                                                     f"Billboard charts" )
    playlist_id = playlist["id"]
    print("searching for songs.....")

    for song in songs :
        track= sp.search(
            q=f"track:{song} year:{time[0]-5}-{time[0]+5}",

            type="track",
            limit= 10,
            market="NG",
        )
        try:
            song_url = track["tracks"]["items"][0]["external_urls"]["spotify"]
        except IndexError:
            print(f"Couldn't find {song}")
            no_of_songs -= 1
        else:
            songs_list.append(song_url)
        finally:
            cronos.sleep(0.2)

    # REDUNDANT CODE !
    # playlists =sp.current_user_playlists(
    #     limit=40,
    # )
    # playlist_id = playlists["items"][0]["id"]

    sp.playlist_add_items(
        playlist_id=playlist_id,
        items=songs_list,)

    print(f"\nPlaylist created successfully!\nI managed to add {no_of_songs} songs")

def program_run():

    start = cronos.time()
    time = time_of_songs()
    url = f"https://www.billboard.com/charts/hot-100/{time[0]}-{time[1]}-{time[2]}/"
    song_data = webscrape_billboard_charts(url)
    create_spotify_playlist(songs=song_data, time=time)

    stop = cronos.time()
    time_taken = round((stop - start)/ 60, 2)
    print(f"The Program took {time_taken} minutes to execute")
    query = input("\n\nDo you want to create another playlist? (Yes or No): ")
    if query.lower() == "yes":
        program_run()

program_run()