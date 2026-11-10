"""Download the FINSABER price file from Hugging Face.

Usage:
    python src/download_finsaber.py

Source: https://huggingface.co/datasets/waylonli/FINSABER-data (Apache-2.0).
The file has daily prices for S&P 500 companies from 2000 to 2024. It
includes companies that were later delisted. No account and no key are
necessary. The file is about 250 MB and goes to data/finsaber/prices.csv.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import requests

REPO = "waylonli/FINSABER-data"
API = f"https://huggingface.co/api/datasets/{REPO}/tree/main?recursive=true"
FILE = f"https://huggingface.co/datasets/{REPO}/resolve/main/"
OUT = Path(__file__).resolve().parent.parent / "data" / "finsaber" / "prices.csv"


def find_price_file() -> tuple[str, int]:
    """Return (path, size) of the price CSV in the dataset."""
    files = requests.get(API, timeout=60).json()
    found = [f for f in files if f.get("type") == "file" and f["path"].lower().endswith(".csv")]
    print("CSV files in the dataset:")
    for f in found:
        print(f"  {f['path']}  ({f.get('size', 0) / 1e6:.0f} MB)")
    prices = [f for f in found if "price" in f["path"].lower()]
    if not prices:
        raise SystemExit("No price CSV found. Send the list above to fix the script.")
    best = max(prices, key=lambda f: ("delist" in f["path"].lower(), f.get("size", 0)))
    return best["path"], int(best.get("size", 0))


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUT.exists():
        path, size = find_price_file()
        print(f"Download {path} ...", flush=True)
        part = OUT.with_suffix(".part")
        done = 0
        with requests.get(FILE + path, stream=True, timeout=120) as response:
            response.raise_for_status()
            with open(part, "wb") as handle:
                for chunk in response.iter_content(chunk_size=1 << 20):
                    handle.write(chunk)
                    done += len(chunk)
                    if size and done % (25 << 20) < (1 << 20):
                        print(f"  {done / 1e6:.0f} of {size / 1e6:.0f} MB", flush=True)
        part.rename(OUT)

    frame = pd.read_csv(OUT, nrows=200_000)
    print(f"Saved {OUT.relative_to(OUT.parent.parent.parent)}  ({OUT.stat().st_size / 1e6:.0f} MB)")
    print("Columns:", list(frame.columns))
    print(frame.head(3).to_string())
    print("Next step: python src/random_portfolios.py finsaber")
    return 0


if __name__ == "__main__":
    sys.exit(main())
