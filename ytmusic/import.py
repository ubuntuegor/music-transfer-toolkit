# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ytmusicapi>=1.11.5",
# ]
# ///

import csv
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
import sys

from ytmusicapi import YTMusic, LikeStatus

from common import get_artist_str


def main() -> None:
    ytmusic = YTMusic("browser.json")

    if len(sys.argv) != 3:
        print("arguments: <path to the csv> <playlist id from the url>")
        return

    songs = read_songs_to_import(sys.argv[1])
    playlist_id = sys.argv[2]

    result_file_name = (
        f"YouTubeMusicImportResults-{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"
    )
    with open(result_file_name, "w", newline="", encoding="utf-8") as result_file:
        w = csv.writer(result_file)
        w.writerow(
            [
                "Title",
                "Album",
                "Artist",
                "ArtworkURL",
                "ResultTitle",
                "ResultAlbum",
                "ResultArtist",
                "ResultArtworkURL",
                "VideoId",
            ]
        )

        for i, song in enumerate(songs):
            result_song = get_result_song(ytmusic, song)
            print(f"({i + 1}/{len(songs)}) {song} => {result_song}")

            if result_song is not None:
                add_song_to_playlist(ytmusic, result_song, playlist_id)
                w.writerow(
                    [
                        song.title,
                        song.album,
                        song.artist,
                        song.artwork_url,
                        result_song.title,
                        result_song.album,
                        result_song.artist,
                        result_song.artwork_url,
                        result_song.video_id,
                    ]
                )
            else:
                w.writerow(
                    [
                        song.title,
                        song.album,
                        song.artist,
                        song.artwork_url,
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )


def add_song_to_playlist(ytmusic, result_song, playlist_id):
    if playlist_id == "LM":
        ytmusic.rate_song(result_song.video_id, LikeStatus.LIKE)
    else:
        ytmusic.add_playlist_items(playlist_id, [result_song.video_id])


def get_result_song(ytmusic, song):
    query = prepare_query(f"{song.artist} {song.title}")
    results = ytmusic.search(query, "songs")
    results = list(filter(lambda x: x["album"] is not None, results))

    if len(results) > 0:
        result = choose_best_result(song, results)
        artist_str = get_artist_str(result)
        return ResultSong(
            result["videoId"],
            result["title"],
            result["album"]["name"],
            artist_str,
            result["thumbnails"][0]["url"],
        )

    return None


def choose_best_result(song, results):
    def similarity(result):
        artist_str = get_artist_str(result)
        return (
            SequenceMatcher(None, song.title.lower(), result["title"].lower()).ratio()
            * 2
            + SequenceMatcher(
                None, song.album.lower(), result["album"]["name"].lower()
            ).ratio()
            + SequenceMatcher(
                lambda c: not c.isalnum(), song.artist.lower(), artist_str.lower()
            ).ratio()
        )

    return max(results, key=similarity)


def prepare_query(query):
    # remove "-" in front of keywords as the search will try to exclude the word
    return " ".join(map(lambda x: x.lstrip("-"), query.split()))


def read_songs_to_import(path):
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return [
            Song(x["Title"], x["Album"], x["Artist"], x["ArtworkURL"]) for x in reader
        ]


@dataclass
class Song:
    title: str
    album: str
    artist: str
    artwork_url: str


@dataclass
class ResultSong:
    video_id: str
    title: str
    album: str
    artist: str
    artwork_url: str


if __name__ == "__main__":
    main()
