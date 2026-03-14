def get_artist_str(result):
    return (
        ", ".join(map(lambda x: x["name"], result["artists"]))
        if "artists" in result
        else ""
    )
