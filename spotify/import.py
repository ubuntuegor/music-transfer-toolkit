# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "spotipy>=2.26.0",
# ]
# ///

import csv
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth


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
    if (
        len(sys.argv) not in range(2, 4)
        or sys.argv[1] == "-h"
        or sys.argv[1] == "--help"
    ):
        print("usage: import.py <tracks_csv> [<playlist_id>]")
        print()
        print("       if <playlist_id> is omitted, tracks are added to Liked Songs")
        return

    scope = "user-library-modify"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    songs = read_songs_to_import(sys.argv[1])
    playlist_id = sys.argv[2] if len(sys.argv) == 3 else None

    result_file_name = (
        f"SpotifyImportResults-{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"
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
                "SpotifyId",
            ]
        )

        for i, song in enumerate(songs):
            result_song = get_result_song(sp, song)
            print(f"({i + 1}/{len(songs)}) {song} => {result_song}")

            if result_song is not None:
                add_song_to_playlist(sp, result_song, playlist_id)
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
                        result_song.spotify_id,
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
class SpotifySong(Song):
    spotify_id: str


def add_song_to_playlist(
    sp: spotipy.Spotify, result_song: SpotifySong, playlist_id: str | None
):
    if playlist_id is None:
        sp.current_user_saved_tracks_add([result_song.spotify_id])
    else:
        sp.playlist_add_items(playlist_id, [result_song.spotify_id])


def get_result_song(sp: spotipy.Spotify, song: Song):
    results = sp.search(f"{song.artist} {song.title}", type="track")
    results = results["tracks"]["items"]
    results = list(
        map(
            lambda x: SpotifySong(
                x["name"],
                x["album"]["name"],
                get_artist_str(x),
                x["album"]["images"][0]["url"] if len(x["album"]["images"]) > 0 else "",
                x["id"],
            ),
            results,
        )
    )

    return choose_best_result(song, results)


def get_artist_str(result):
    return ", ".join(map(lambda x: x["name"], result["artists"]))


def prepare_query(query):
    # remove "feat" as it confuses spotify's search
    return " ".join(filter(lambda x: x != "(feat." and x != "feat.", query.split()))


if __name__ == "__main__":
    main()
