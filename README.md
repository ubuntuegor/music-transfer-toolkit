# Music Transfer Toolkit

Tools to transfer music across various streaming services.

Some of these scripts use `uv` for easier dependency management. Run them like this:

```
uv run --script <script.py> ...<args>
```

## Tools:

- Reverse CSV - reverse playlist to import it in the correct order
- Diff from CSV - used to check the import results and find songs that might've been mismatched
- Per each streaming service:
    - Clear liked songs
    - Export tracks from playlist
    - Import tracks into playlist

## Workflow

1. Export songs from an old streaming service
2. (Optional) Use the clean script for the new streaming service to have a fresh start
3. Import songs into the new streaming service using the previously exported CSV
4. Use the diff script to check that matching songs were correctly found

## Tracks exchange format

- Format: CSV
- Fields:
    - `Title` - Track title
    - `Album` - Album name
    - `Artist` - Artist name(s)
    - `ArtworkURL` - URL to the artwork image, used for comparison, better if small
    - Any extra service-specific columns

## Import results format

- Format: CSV
- Fields:
    - `Title`
    - `Album`
    - `Artist`
    - `ArtworkURL`
    - `ResultTitle` - empty if not found
    - `ResultAlbum` - empty if not found
    - `ResultArtist` - empty if not found
    - `ResultArtworkURL` - empty if not found
    - Any extra service-specific columns from the resulting service
