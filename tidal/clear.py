# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "tidalapi>=0.8.11",
# ]
# ///

from pathlib import Path

import tidalapi


def main() -> None:
    tidal = tidalapi.session.Session()
    tidal.login_session_file(Path("session.json"))

    offset = 0
    total = tidal.user.favorites.get_tracks_count()

    while offset < total:
        print(f"{offset}/{total}")

        results = tidal.user.favorites.tracks(limit=50, offset=offset)

        for result in results:
            tidal.user.favorites.remove_track(result.id)

        offset += 50


if __name__ == "__main__":
    main()
