"""Compare the FINSABER prices with the Yahoo prices.

Usage:
    python src/compare_sources.py

The FINSABER page does not name its price source. This script compares the
two sources for each ticker that is in both. It uses the daily returns in
the period that both sources cover.

Output: results/source_check.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import random_portfolios as rp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    yahoo = rp.load_yahoo(ROOT / "data" / "universe")
    finsaber = rp.load_finsaber(ROOT / "data" / "finsaber" / "prices.csv")
    shared = sorted(set(yahoo.columns) & set(finsaber.columns))
    days = yahoo.index.intersection(finsaber.index)
    rows = []
    for ticker in shared:
        a = yahoo.loc[days, ticker].dropna()
        b = finsaber.loc[days, ticker].dropna()
        both = a.index.intersection(b.index)
        if len(both) < 250:
            continue
        ra, rb = a[both].pct_change().dropna(), b[both].pct_change().dropna()
        growth_a, growth_b = a[both].iloc[-1] / a[both].iloc[0], b[both].iloc[-1] / b[both].iloc[0]
        rows.append({
            "ticker": ticker,
            "days": int(len(both)),
            "return_correlation": round(float(np.corrcoef(ra, rb)[0, 1]), 4),
            "days_with_return_gap_above_1pct": int((abs(ra - rb) > 0.01).sum()),
            "growth_yahoo": round(float(growth_a), 3),
            "growth_finsaber": round(float(growth_b), 3),
            "growth_ratio": round(float(growth_b / growth_a), 3),
        })
    correlations = [r["return_correlation"] for r in rows]
    ratios = [r["growth_ratio"] for r in rows]
    out = {
        "tickers_in_both": len(rows),
        "period": [str(days[0].date()), str(days[-1].date())] if len(days) else [],
        "median_return_correlation": round(float(np.median(correlations)), 4),
        "tickers_with_correlation_below_0.98": [r["ticker"] for r in rows if r["return_correlation"] < 0.98],
        "median_growth_ratio": round(float(np.median(ratios)), 3),
        "tickers_with_growth_gap_above_5pct": [r["ticker"] for r in rows if abs(r["growth_ratio"] - 1) > 0.05],
        "by_ticker": rows,
    }
    (ROOT / "results" / "source_check.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "by_ticker"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
