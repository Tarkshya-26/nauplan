import argparse

from nauplan import routing
from nauplan.data import fetch


def main() -> None:
    parser = argparse.ArgumentParser(prog="nauplan")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="download all public data sources into data/raw")
    sub.add_parser("distances", help="recompute load-to-discharge sea distances into reference/distances.csv")
    args = parser.parse_args()
    if args.cmd == "fetch":
        for name, path in fetch.fetch_all().items():
            print(f"{name:16} -> {path}")
    elif args.cmd == "distances":
        print(routing.write_distances())
