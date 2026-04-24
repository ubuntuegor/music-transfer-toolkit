# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "tidalapi>=0.8.11",
# ]
# ///

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys

import tidalapi
from tidalapi.types import ItemOrder


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
        print(
            "       if <playlist_id> is omitted, tracks from your collection are exported"
        )
        return

    tidal = tidalapi.session.Session()
    tidal.login_session_file(Path("session.json"))

    playlist_id = sys.argv[1] if len(sys.argv) > 1 else None

    csv_file_name = (
        f"TidalExport-{playlist_id}-{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"
    )
    with open(csv_file_name, "w", newline="", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        w.writerow(
            [
                "Title",
                "Album",
                "Artist",
                "ArtworkURL",
                "TidalId",
            ]
        )

        offset = 0
        total = None

        if playlist_id is None:
            total = tidal.user.favorites.get_tracks_count()
        else:
            total = tidal.playlist(playlist_id).get_tracks_count()

        while offset < total:
            print(f"{offset}/{total}")

            results = []

            if playlist_id is None:
                results = tidal.user.favorites.tracks(
                    limit=50, offset=offset, order=ItemOrder.Date
                )
            else:
                results = tidal.playlist(playlist_id).tracks(
                    limit=50, offset=offset, order=ItemOrder.Index
                )

            for result in results:
                song = parse_song(result)
                w.writerow(
                    [
                        song.title,
                        song.album,
                        song.artist,
                        song.artwork_url,
                        song.tidal_id,
                    ]
                )

            offset += 50


def parse_song(x: tidalapi.media.Track):
    return TidalSong(
        x.full_name,
        x.album.name,
        get_artist_str(x),
        get_artwork_url(x),
        x.id,
    )


def get_artwork_url(result: tidalapi.media.Track):
    try:
        return result.album.image(80)
    except:
        return ""


def get_artist_str(result: tidalapi.media.Track):
    return ", ".join(map(lambda x: x.name, result.artists))


@dataclass
class TidalSong(Song):
    tidal_id: str


if __name__ == "__main__":
    main()
