import argparse

from nauplan.data import fetch


def main() -> None:
    parser = argparse.ArgumentParser(prog="nauplan")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="download all public data sources into data/raw")
    args = parser.parse_args()
    if args.cmd == "fetch":
        for name, path in fetch.fetch_all().items():
            print(f"{name:16} -> {path}")
