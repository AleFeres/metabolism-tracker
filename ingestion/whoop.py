import argparse, datetime as dt, pandas as pd, requests
from pathlib import Path
from .auth import get_access_token

BASE = "https://api.prod.whoop.com/developer/v1"
DEST = Path("data/raw")


def fetch_cycles(day: dt.date):
    hdr = {"Authorization": f"Bearer {get_access_token()}"}
    start = dt.datetime.combine(day, dt.time.min).isoformat()
    end   = dt.datetime.combine(day, dt.time.max).isoformat()
    url = f"{BASE}/cycle"
    params = {"start": start, "end": end, "limit": 25}
    records = []
    while True:
        r = requests.get(url, headers=hdr, params=params, timeout=30).json()
        records.extend(r.get("records", []))
        nxt = r.get("next_token")
        if not nxt:
            break
        params["nextToken"] = nxt
    return pd.json_normalize(records)


def main(date):
    day = dt.date.fromisoformat(date)
    df = fetch_cycles(day)
    DEST.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DEST / f"whoop_cycles_{day}.parquet", compression="zstd")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.date.today().isoformat())
    main(**vars(parser.parse_args()))
