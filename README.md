# Music Transfer Toolkit

Tools to transfer music from and to various streaming services.

## Tools:

- Clean playlist
- Export tracks from playlist
- Import tracks into playlist

## Tracks exchange format

- Format: CSV
- Fields:
    - `Title` - Track title
    - `Album` - Album name
    - `Artist` - Artist(s) name
    - Any extra service-specific columns

## Import results format

- Format: CSV
- Fields:
    - `Title`
    - `Album`
    - `Artist`
    - `ResultTitle` - may be empty
    - `ResultAlbum` - may be empty
    - `ResultArtist` - may be empty
    - Any extra service-specific columns from the resulting service
