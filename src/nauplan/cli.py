import argparse

from nauplan import routing
from nauplan.data import fetch


def main() -> None:
    parser = argparse.ArgumentParser(prog="nauplan")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="download all public data sources into data/raw")
    sub.add_parser("distances", help="recompute load-to-discharge sea distances into reference/distances.csv")
    sub.add_parser("backtest", help="walk-forward backtest of freight models; writes reports/backtest.md")
    sub.add_parser("forecast", help="latest freight forecast; writes data/processed/forecast_latest.json")
    sub.add_parser("plan", help="vessel choice and charter plan for the programme; writes reports/plan_example.md")
    args = parser.parse_args()
    if args.cmd == "fetch":
        for name, path in fetch.fetch_all().items():
            print(f"{name:16} -> {path}")
    elif args.cmd == "distances":
        print(routing.write_distances())
    elif args.cmd == "backtest":
        from nauplan.forecast.run import backtest_report
        print(backtest_report())
    elif args.cmd == "forecast":
        from nauplan.forecast.run import latest_forecast
        print(latest_forecast())
    elif args.cmd == "plan":
        from nauplan.optimise.report import plan_report
        print(plan_report())
