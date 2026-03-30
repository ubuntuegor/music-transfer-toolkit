# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import sys


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print("usage: reverse_csv.py <input_csv> <output_csv>")
        return

    lines = open(sys.argv[1], encoding="utf-8").readlines()
    header = lines[0]
    rest = lines[1:]
    rest = rest[::-1]
    open(sys.argv[2], "w", encoding="utf-8").writelines([header] + rest)


if __name__ == "__main__":
    main()
