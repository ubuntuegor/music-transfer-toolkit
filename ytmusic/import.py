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


# COMMON


@dataclass
class Song:
    title: str
    album: str
    artist: str
    artwork_url: str


def read_songs_to_import(path):
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return [
            Song(x["Title"], x["Album"], x["Artist"], x["ArtworkURL"]) for x in reader
        ]


def compare_songs(a: Song, b: Song) -> float:
    return (
        SequenceMatcher(None, a.title.lower(), b.title.lower()).ratio() * 2
        + SequenceMatcher(None, a.album.lower(), b.album.lower()).ratio()
        + SequenceMatcher(
            lambda c: not c.isalnum(), a.artist.lower(), b.artist.lower()
        ).ratio()
    )


def choose_best_result(song: Song, results: list[Song]) -> Song | None:
    return max(results, key=lambda x: compare_songs(song, x), default=None)


# /COMMON


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print("usage: import.py <tracks_csv> <playlist_id>")
        return

    ytmusic = YTMusic("browser.json")

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


@dataclass
class YTMusicSong(Song):
    video_id: str


def add_song_to_playlist(ytmusic, result_song, playlist_id):
    if playlist_id == "LM":
        ytmusic.rate_song(result_song.video_id, LikeStatus.LIKE)
    else:
        ytmusic.add_playlist_items(playlist_id, [result_song.video_id])


def get_result_song(ytmusic, song):
    query = prepare_query(f"{song.artist} {song.title}")
    results = ytmusic.search(query, "songs")
    results = list(filter(lambda x: x["album"] is not None, results))
    results = list(
        map(
            lambda x: YTMusicSong(
                x["title"],
                x["album"]["name"],
                get_artist_str(x),
                x["thumbnails"][0]["url"],
                x["videoId"],
            ),
            results,
        )
    )

    return choose_best_result(song, results)


def get_artist_str(result):
    return (
        ", ".join(map(lambda x: x["name"], result["artists"]))
        if "artists" in result
        else ""
    )


def prepare_query(query):
    # remove "-" in front of keywords as the search will try to exclude the word
    return " ".join(map(lambda x: x.lstrip("-"), query.split()))


if __name__ == "__main__":
    main()
