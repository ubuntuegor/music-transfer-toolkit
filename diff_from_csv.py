# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "beautifulsoup4>=4.14.3",
# ]
# ///

import csv
from dataclasses import dataclass
from difflib import SequenceMatcher
import sys
from bs4 import BeautifulSoup


BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
    <style>
        body {
            grid-template-columns: 1fr 90% 1fr;
        }

        mark.added {
            background-color: #61ff61;
        }

        mark.removed {
            background-color: #ff4f4f;
        }
    </style>
    <title>Diff</title>
</head>
<body>
    <table>
        <thead>
            <tr>
                <th>№</th>
                <th>Art</th>
                <th>Title</th>
                <th>Album</th>
                <th>Artist</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>
</body>
</html>
"""


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print("usage: diff_from_csv.py <path_to_import_results_csv> <path_to_html_result>")
        return

    csvfilepath = sys.argv[1]

    results = []
    with open(csvfilepath, encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for r in reader:
            results.append(
                ImportResult(
                    r["Title"],
                    r["Album"],
                    r["Artist"],
                    r["ArtworkURL"],
                    r["ResultTitle"],
                    r["ResultAlbum"],
                    r["ResultArtist"],
                    r["ResultArtworkURL"],
                )
            )

    html = BeautifulSoup(BASE_HTML, "html.parser")

    for i, result in enumerate(results):
        html.tbody.append(create_row_for_result(i, result))

    open(sys.argv[2], "w", encoding="utf-8").write(str(html))


def create_row_for_result(i, result):
    html = BeautifulSoup("<tr></tr>", "html.parser")

    html.tr.append(html.new_tag("td", string=str(i + 1)))

    orig_img = html.new_tag(
        "img", loading="lazy", width="40", height="40", src=result.artwork_url
    )
    result_img = html.new_tag(
        "img", loading="lazy", width="40", height="40", src=result.result_artwork_url
    )
    art_td = html.new_tag("td", style="font-size: 0")
    art_td.append(orig_img)
    art_td.append(result_img)
    html.tr.append(art_td)

    html.tr.append(create_cell_for_string_diff(result.title, result.result_title))

    html.tr.append(create_cell_for_string_diff(result.album, result.result_album))

    html.tr.append(create_cell_for_string_diff(result.artist, result.result_artist))

    return html.tr


def create_cell_for_string_diff(before, after):
    html = BeautifulSoup("<td></td>", "html.parser")
    old_name = html.new_tag("div")
    new_name = html.new_tag("div")

    blocks = SequenceMatcher(None, before.lower(), after.lower()).get_matching_blocks()

    i = 0
    j = 0

    for block in blocks:
        ii, jj, nn = block
        to_remove = before[i:ii]
        to_add = after[j:jj]

        if len(to_remove) > 0:
            mark = html.new_tag("mark", string=to_remove)
            mark["class"] = "removed"
            old_name.append(mark)

        if len(to_add) > 0:
            mark = html.new_tag("mark", string=to_add)
            mark["class"] = "added"
            new_name.append(mark)

        old_name.append(before[ii : ii + nn])
        new_name.append(after[jj : jj + nn])

        i = ii + nn
        j = jj + nn

    html.td.append(old_name)
    html.td.append(new_name)

    return html.td


@dataclass
class ImportResult:
    title: str
    album: str
    artist: str
    artwork_url: str
    result_title: str
    result_album: str
    result_artist: str
    result_artwork_url: str


if __name__ == "__main__":
    main()
