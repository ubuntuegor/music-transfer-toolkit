# Spotify

## Clear

Just select all tracks in the desktop app -> right-click -> remove

## Setup

[Create an app here](https://developer.spotify.com/dashboard/applications), then set the following environment variables:
- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `SPOTIPY_REDIRECT_URI` - use something like `http://127.0.0.1:9090` - the script will listen on this port automatically. Make sure to set the same URI in the Spotify dashboard
