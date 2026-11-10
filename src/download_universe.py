"""Download the prices for the random-portfolio test.

Usage:
    python src/download_universe.py

Source: Yahoo Finance through the free yfinance package. No account, no key.
The prices are adjusted for splits and dividends. One CSV file for each
ticker goes into data/universe/. The run is resumable.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import universe  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "data" / "universe"
START = "2012-01-01"   # the volatility median needs two years before 2015


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    missing = []
    for ticker in universe.DOWNLOAD:
        path = OUT / f"{ticker}.csv"
        if path.exists():
            continue
        frame = yf.Ticker(ticker).history(start=START, auto_adjust=True)
        if frame.empty:
            missing.append(ticker)
            print(f"  {ticker}: no data", flush=True)
            continue
        frame.index = frame.index.strftime("%Y-%m-%d")
        frame[["Close"]].to_csv(path, index_label="Date")
        print(f"  {ticker}: {len(frame)} days", flush=True)
        time.sleep(0.5)
    (OUT / "missing.txt").write_text("\n".join(missing) + ("\n" if missing else ""))
    have = len(list(OUT.glob("*.csv")))
    print(f"Done. {have} price files in data/universe/. {len(missing)} tickers had no data.")
    print("Next step: python src/random_portfolios.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
