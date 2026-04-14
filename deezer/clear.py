# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "deezer-python>=7.2.0",
# ]
# ///

import os

import deezer


def main() -> None:
    if "DEEZER_ACCESS_TOKEN" not in os.environ:
        raise RuntimeError("set DEEZER_ACCESS_TOKEN environment variable")
    client = deezer.Client(access_token=os.environ["DEEZER_ACCESS_TOKEN"])
    tracks = list(client.get_user_tracks())
    total = len(tracks)

    for i, track in enumerate(tracks):
        client.remove_user_track(track.id)
        print(f"Removed {i + 1}/{total}")


if __name__ == "__main__":
    main()
