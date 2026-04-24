# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "tidalapi>=0.8.11",
# ]
# ///

import csv
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
import sys

import tidalapi


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
    filtered = filter(lambda x: compare_songs(song, x) >= 2, results)
    return max(filtered, key=lambda x: compare_songs(song, x), default=None)


# /COMMON


def main() -> None:
    if (
        len(sys.argv) not in range(2, 4)
        or sys.argv[1] == "-h"
        or sys.argv[1] == "--help"
    ):
        print("usage: import.py <tracks_csv> [<playlist_id>]")
        print()
        print("       if <playlist_id> is omitted, tracks are added to Collection")
        return

    tidal = tidalapi.session.Session()
    tidal.login_session_file(Path("session.json"))

    songs = read_songs_to_import(sys.argv[1])
    playlist_id = sys.argv[2] if len(sys.argv) == 3 else None

    result_file_name = (
        f"TidalImportResults-{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"
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
                "TidalId",
            ]
        )

        for i, song in enumerate(songs):
            result_song = get_result_song(tidal, song)
            print(f"({i + 1}/{len(songs)}) {song} => {result_song}")

            if result_song is not None:
                add_song_to_playlist(tidal, result_song, playlist_id)
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
                        result_song.tidal_id,
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
class TidalSong(Song):
    tidal_id: str


def add_song_to_playlist(
    client: tidalapi.session.Session, result_song: TidalSong, playlist_id: str | None
):
    if playlist_id is None:
        client.user.favorites.add_track(result_song.tidal_id)
    else:
        playlist = client.playlist(playlist_id)
        playlist.add([result_song.tidal_id])


def get_result_song(client: tidalapi.session.Session, song: Song):
    results = client.search(
        f"{song.artist} {song.title}", models=[tidalapi.media.Track], limit=50
    )["tracks"]
    results = list(
        map(
            lambda x: TidalSong(
                x.full_name,
                x.album.name,
                get_artist_str(x),
                get_artwork_url(x),
                x.id,
            ),
            results,
        )
    )

    return choose_best_result(song, results)


def get_artwork_url(result: tidalapi.media.Track):
    return result.album.image(80)


def get_artist_str(result: tidalapi.media.Track):
    return ", ".join(map(lambda x: x.name, result.artists))


if __name__ == "__main__":
    main()
