# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "deezer-python>=7.2.0",
# ]
# ///

import csv
from dataclasses import dataclass
from datetime import datetime
import os
import sys

import deezer


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

    if "DEEZER_ACCESS_TOKEN" not in os.environ:
        raise RuntimeError("set DEEZER_ACCESS_TOKEN environment variable")
    client = deezer.Client(access_token=os.environ["DEEZER_ACCESS_TOKEN"])

    playlist_id = sys.argv[1] if len(sys.argv) > 1 else None

    csv_file_name = (
        f"DeezerExport-{playlist_id}-{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"
    )
    with open(csv_file_name, "w", newline="", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        w.writerow(
            [
                "Title",
                "Album",
                "Artist",
                "ArtworkURL",
                "DeezerId",
            ]
        )

        results = None

        if playlist_id is None:
            results = client.get_user_tracks()
        else:
            playlist = client.get_playlist(playlist_id)
            results = playlist.get_tracks()

        for i, result in enumerate(results):
            print(f"writing song {i + 1}")
            song = parse_song(result)
            w.writerow(
                [
                    song.title,
                    song.album,
                    song.artist,
                    song.artwork_url,
                    song.deezer_id,
                ]
            )


def parse_song(result):
    return DeezerSong(
        result.title,
        result.album.title,
        get_artist_str(result),
        get_artwork_url(result),
        result.id,
    )


def get_artwork_url(result):
    try:
        return result.album.cover_small
    except:
        return ""


def get_artist_str(result):
    if hasattr(result, "contributors"):
        return ", ".join(map(lambda x: x.name, result.contributors))
    else:
        return result.artist.name


@dataclass
class DeezerSong(Song):
    deezer_id: str


if __name__ == "__main__":
    main()
