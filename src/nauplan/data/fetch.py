"""Fetchers for the free, public data sources used by the prototype.

Each fetcher returns a tidy DataFrame and `save` writes it to data/raw as parquet.
Sources and their limits are documented in docs/data-sources.md.
"""
from __future__ import annotations

import io
import re

import httpx
import pandas as pd

from nauplan.config import RAW
from nauplan.reference import discharge_ports

# FRED silently stalls requests with unfamiliar User-Agents, so keep the httpx default.

TIMEOUT = 60

FRED_SERIES = {
    "brent_usd_bbl": "DCOILBRENTEU",  # Brent crude, daily; proxy for bunker fuel cost
    "usd_inr": "DEXINUS",  # INR per USD, daily
}

PINK_SHEET_PAGE = "https://www.worldbank.org/en/research/commodity-markets"
PINK_SHEET_COLUMNS = {
    "Coal, Australian": "coal_australia_usd_t",
    "Coal, South African **": "coal_south_africa_usd_t",
    "Iron ore, cfr spot": "iron_ore_cfr_usd_t",
    "Crude oil, Brent": "brent_usd_bbl",
}

MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
# ERA5 ocean reanalysis: consistent history back to 2018 (the default model starts Oct 2021).
# It only provides total wave height; swell and wind-wave splits come back empty.
MARINE_MODEL = "era5_ocean"
MARINE_DAILY = ["wave_height_max"]


def fetch_bdry(start: str = "2018-01-01") -> pd.DataFrame:
    """Breakwave Dry Bulk Shipping ETF (BDRY), daily close.

    BDRY holds dry bulk freight futures, so it tracks the direction of the freight
    market. It is a blended market proxy, not a per-vessel-class or per-route rate.
    """
    import yfinance as yf

    df = yf.download("BDRY", start=start, progress=False, auto_adjust=True)
    if df.empty:
        raise RuntimeError("BDRY download returned no rows")
    close = df["Close"]
    if isinstance(close, pd.DataFrame):  # yfinance returns a MultiIndex for single tickers too
        close = close.iloc[:, 0]
    return close.rename("bdry_close").rename_axis("date").reset_index()


def fetch_fred(name: str) -> pd.DataFrame:
    series = FRED_SERIES[name]
    r = httpx.get("https://fred.stlouisfed.org/graph/fredgraph.csv", params={"id": series}, timeout=TIMEOUT)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["date", name]
    df["date"] = pd.to_datetime(df["date"])
    df[name] = pd.to_numeric(df[name], errors="coerce")  # FRED marks holidays with "."
    return df.dropna()


def pink_sheet_url() -> str:
    """The workbook URL changes with every monthly update, so read it off the landing page."""
    r = httpx.get(PINK_SHEET_PAGE, timeout=TIMEOUT, follow_redirects=True)
    r.raise_for_status()
    m = re.search(r'https://[^"]*CMO-Historical-Data-Monthly\.xlsx', r.text)
    if not m:
        raise RuntimeError("Pink Sheet link not found on the World Bank page")
    return m.group(0)


def parse_pink_sheet(raw: pd.DataFrame) -> pd.DataFrame:
    """Parse the 'Monthly Prices' sheet read with header=None.

    Row 4 holds series names, row 5 units, data starts at row 6 with dates like '2026M08'.
    """
    names = raw.iloc[4]
    keep = {i: PINK_SHEET_COLUMNS[n] for i, n in names.items() if n in PINK_SHEET_COLUMNS}
    body = raw.iloc[6:, [0, *keep]].copy()
    body.columns = ["month", *keep.values()]
    body = body[body["month"].astype(str).str.match(r"^\d{4}M\d{2}$")]
    body["date"] = pd.to_datetime(body["month"].str.replace("M", "-") + "-01")
    for c in keep.values():
        body[c] = pd.to_numeric(body[c], errors="coerce")  # '…' marks missing values
    return body.drop(columns="month")[["date", *keep.values()]].reset_index(drop=True)


def fetch_pink_sheet() -> pd.DataFrame:
    r = httpx.get(pink_sheet_url(), timeout=TIMEOUT, follow_redirects=True)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), sheet_name="Monthly Prices", header=None)
    return parse_pink_sheet(raw)


def fetch_marine(start: str = "2018-01-01", end: str | None = None) -> pd.DataFrame:
    """Daily sea state off each East Coast discharge port (Open-Meteo Marine API)."""
    end = end or (pd.Timestamp.today() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    frames = []
    for port in discharge_ports().itertuples():
        r = httpx.get(MARINE_URL, timeout=TIMEOUT, params={
            "latitude": port.lat, "longitude": port.lon, "daily": ",".join(MARINE_DAILY), "models": MARINE_MODEL,
            "start_date": start, "end_date": end, "timezone": "Asia/Kolkata",
        })
        r.raise_for_status()
        d = pd.DataFrame(r.json()["daily"]).rename(columns={"time": "date"})
        d["date"] = pd.to_datetime(d["date"])
        d.insert(1, "port", port.port_id)
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def save(df: pd.DataFrame, name: str) -> str:
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return str(path)


def fetch_all() -> dict[str, str]:
    out = {"bdry": save(fetch_bdry(), "bdry")}
    for name in FRED_SERIES:
        out[name] = save(fetch_fred(name), name)
    out["pink_sheet"] = save(fetch_pink_sheet(), "pink_sheet")
    out["marine"] = save(fetch_marine(), "marine")
    return out
