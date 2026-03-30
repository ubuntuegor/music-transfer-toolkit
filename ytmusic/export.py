# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ytmusicapi>=1.11.5",
# ]
# ///

import csv
from dataclasses import dataclass
from datetime import datetime
import sys

from ytmusicapi import YTMusic

# COMMON


@dataclass
class Song:
    title: str
    album: str
    artist: str
    artwork_url: str


# /COMMON


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print("usage: export.py <playlist_id>")
        return

    ytmusic = YTMusic("browser.json")

    playlist_id = sys.argv[1]
    results = ytmusic.get_playlist(playlist_id, None)["tracks"]

    csv_file_name = f"YouTubeMusicExport-{playlist_id}-{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"
    with open(csv_file_name, "w", newline="", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        w.writerow(
            [
                "Title",
                "Album",
                "Artist",
                "ArtworkURL",
                "VideoId",
            ]
        )

        for result in results:
            song = parse_song(result)
            w.writerow(
                [song.title, song.album, song.artist, song.artwork_url, song.video_id]
            )


def parse_song(result):
    artist_str = get_artist_str(result)
    album_str = result["album"]["name"] if result["album"] is not None else ""
    return YTMusicSong(
        result["title"],
        album_str,
        artist_str,
        result["thumbnails"][0]["url"],
        result["videoId"],
    )


def get_artist_str(result):
    return (
        ", ".join(map(lambda x: x["name"], result["artists"]))
        if "artists" in result
        else ""
    )


@dataclass
class YTMusicSong(Song):
    video_id: str


if __name__ == "__main__":
    main()
