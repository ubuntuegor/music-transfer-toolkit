# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "spotipy>=2.26.0",
# ]
# ///

import csv
from dataclasses import dataclass
from datetime import datetime
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


# /COMMON


def main() -> None:
    if len(sys.argv) > 2 or (
        len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help")
    ):
        print("usage: export.py [<playlist_id>]")
        print()
        print("       if <playlist_id> is omitted, Liked Songs are exported")
        return

    scope = "user-library-modify"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    playlist_id = sys.argv[1] if len(sys.argv) > 1 else None

    csv_file_name = f"SpotifyExport-{playlist_id}-{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"
    with open(csv_file_name, "w", newline="", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        w.writerow(
            [
                "Title",
                "Album",
                "Artist",
                "ArtworkURL",
                "SpotifyId",
            ]
        )

        offset = 0
        total = None
        while total is None or offset < total:
            print(f"{offset}/{total}")

            results = []

            if playlist_id is None:
                page = sp.current_user_saved_tracks(limit=50, offset=offset)
                total = page["total"]

                results = list(map(lambda x: x["track"], page["items"]))
            else:
                page = sp.playlist_items(playlist_id, limit=50, offset=offset)
                total = page["total"]

                results = list(map(lambda x: x["item"], page["items"]))

            for result in results:
                song = parse_song(result)
                w.writerow(
                    [
                        song.title,
                        song.album,
                        song.artist,
                        song.artwork_url,
                        song.spotify_id,
                    ]
                )

            offset += 50


def parse_song(result):
    return SpotifySong(
        result["name"],
        result["album"]["name"],
        get_artist_str(result),
        result["album"]["images"][0]["url"]
        if len(result["album"]["images"]) > 0
        else "",
        result["id"],
    )


def get_artist_str(result):
    return ", ".join(map(lambda x: x["name"], result["artists"]))


@dataclass
class SpotifySong(Song):
    spotify_id: str


if __name__ == "__main__":
    main()
