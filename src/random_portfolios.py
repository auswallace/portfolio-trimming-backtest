"""The better test: many random portfolios, many start dates.

Usage:
    python src/random_portfolios.py finsaber     # main test
    python src/random_portfolios.py yahoo        # cross-check

One portfolio and one period can show a win by chance. This script asks the
same question many times:

  - 1,000 random portfolios for each start year (6 positions, random weights)
  - each start year gives one 5-year window
  - trades occur on the day after the signal, and proceeds go back pro-rata

For each case it compares two trim rules with buy-and-hold:

  vol_2.5     trim 20% when 30-day volatility is above 2.5x its median
  trim_100    trim 20% when the gain on the cost basis is +100% or more

Two price sources:

  finsaber    S&P 500 companies from 2000, with delisted companies
              (src/download_finsaber.py). A portfolio can only hold companies
              that were in the index on its start date (data/sp500_members.csv).
              When a company leaves the market, its position stays at the
              last price to the end of the window.
  yahoo       103 large companies from the end of 2014, from 2012
              (src/download_universe.py). Companies that left the market are
              not in it.

Output: results/random_portfolios_<source>.json and .csv, two charts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402
import plots  # noqa: E402
import universe  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CHARTS = ROOT / "charts"
MEMBERS = ROOT / "data" / "sp500_members.csv"

SEED = 42
PORTFOLIOS_PER_WINDOW = 1000
POSITIONS = 6
WINDOW_DAYS = 5 * engine.TRADING_DAYS
MIN_TICKERS = 50      # a start year needs this many tickers
INITIAL = 100_000
STRATEGIES = ("vol_2.5", "trim_100")


# ------------------------------------------------------------------ data
def load_yahoo(data_dir: Path) -> pd.DataFrame:
    """One CSV for each ticker (Date, Close)."""
    columns = {}
    for path in sorted(data_dir.glob("*.csv")):
        df = pd.read_csv(path)
        columns[path.stem] = pd.Series(df["Close"].to_numpy(), index=pd.to_datetime(df["Date"]))
    return pd.DataFrame(columns).sort_index()


def load_finsaber(path: Path) -> pd.DataFrame:
    """One long CSV (date, symbol, adjusted_close)."""
    df = pd.read_csv(path)
    df.columns = [c.lower() for c in df.columns]
    price = "adjusted_close" if "adjusted_close" in df.columns else "adj_close"
    symbol = "symbol" if "symbol" in df.columns else "ticker"
    df["date"] = pd.to_datetime(df["date"])
    df = df[df[price] > 0].drop_duplicates(["date", symbol], keep="last")
    return df.pivot(index="date", columns=symbol, values=price).sort_index()


def repair_finsaber(prices: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Remove price series that are not one company.

    Some symbols in the file have bad rows, or a second company uses the
    symbol after the first company left the market. Two rules:

      1. A symbol with 3 or more daily moves above +200% or below -80% is removed.
      2. For the other symbols, the series stops at the first gap of more
         than 30 calendar days, or at the first daily move above +200%.
    """
    removed, cut = [], []
    columns = {}
    for ticker in prices.columns:
        series = prices[ticker].dropna()
        if len(series) < 2:
            continue
        move = series.pct_change()
        if int(((move > 2.0) | (move < -0.8)).sum()) >= 3:
            removed.append(ticker)
            continue
        gap = series.index.to_series().diff().dt.days
        breaks = series.index[((gap > 30) | (move > 2.0)).to_numpy()]
        if len(breaks):
            series = series[series.index < breaks[0]]
            cut.append(ticker)
        columns[ticker] = series
    report = {"symbols_in_file": int(prices.shape[1]), "symbols_removed": len(removed), "symbols_cut_short": len(cut)}
    return pd.DataFrame(columns).sort_index(), report


def clean(prices: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Keep full market days. Hold the last price after a company leaves.

    Returns the price table and the last real price date of each ticker.
    """
    prices = prices.loc[prices.notna().sum(axis=1) >= MIN_TICKERS]
    last_real = prices.apply(lambda column: column.last_valid_index())
    return prices.ffill(), last_real


def members_on(day: pd.Timestamp) -> set[str]:
    """S&P 500 members on one day."""
    table = pd.read_csv(MEMBERS, parse_dates=["start_date", "end_date"])
    inside = (table["start_date"] <= day) & (table["end_date"].isna() | (table["end_date"] > day))
    return set(table.loc[inside, "ticker"])


def window_starts(prices: pd.DataFrame) -> list[int]:
    """Row number of the first trading day of each year that has a full window."""
    starts = []
    for year in range(prices.index[0].year, prices.index[-1].year + 1):
        rows = np.flatnonzero(prices.index.year == year)
        if len(rows) and rows[0] > 0 and rows[0] + WINDOW_DAYS <= len(prices):
            starts.append(int(rows[0]))
    return starts


# ------------------------------------------------------------ simulation
def signals_for(prices, vol_30, vol_median, ticker, strategy, start, end):
    if strategy == "vol_2.5":
        return engine.volatility_signals(
            prices.index, vol_30[ticker].to_numpy(), vol_median[ticker].to_numpy(), 2.5,
            start=start, end=end, warmup=0,
        )
    return engine.threshold_signals(prices[ticker].to_numpy(), 1.00, start=start, end=end)


def one_case(prices, weights, signals, start, end) -> dict:
    """Compare both strategies with buy-and-hold for one portfolio and window."""
    hold = engine.buy_and_hold(prices, weights, INITIAL, start=start, end=end)
    base = engine.metrics(hold, INITIAL)
    px_end = prices[list(weights)].iloc[end - 1].to_numpy()
    px_start = prices[list(weights)].iloc[start].to_numpy()
    growth = np.array(list(weights.values())) * px_end / px_start
    row = {
        "hold_cagr": base["cagr"],
        "hold_sharpe": base["sharpe"],
        "hold_max_drawdown": base["max_drawdown"],
        "largest_position_end": float(growth.max() / growth.sum()),
    }
    for strategy in STRATEGIES:
        sig = {t: signals[strategy][t] for t in weights}
        run = engine.simulate(prices, weights, sig, INITIAL, lag=1, start=start, end=end)
        m = engine.metrics(run["value"], INITIAL)
        row[f"{strategy}_trims"] = len(run["trades"])
        row[f"{strategy}_cagr_diff"] = m["cagr"] - base["cagr"]
        row[f"{strategy}_sharpe_diff"] = m["sharpe"] - base["sharpe"]
        row[f"{strategy}_drawdown_diff"] = m["max_drawdown"] - base["max_drawdown"]
    return row


def summarize(frame: pd.DataFrame, strategy: str) -> dict:
    """Rates for one strategy. A case with no trim is equal to buy-and-hold,
    so the win rates use only the cases with one trim or more."""
    traded = frame[frame[f"{strategy}_trims"] > 0]
    cagr = traded[f"{strategy}_cagr_diff"]
    return {
        "cases": int(len(frame)),
        "cases_with_a_trim": int(len(traded)),
        "beats_on_return_pct": round(float((cagr > 0).mean()) * 100, 1),
        "beats_on_sharpe_pct": round(float((traded[f"{strategy}_sharpe_diff"] > 0).mean()) * 100, 1),
        "smaller_drawdown_pct": round(float((traded[f"{strategy}_drawdown_diff"] > 0).mean()) * 100, 1),
        "median_cagr_diff_points": round(float(cagr.median()) * 100, 2),
        "mean_cagr_diff_points": round(float(cagr.mean()) * 100, 2),
        "p05_cagr_diff_points": round(float(cagr.quantile(0.05)) * 100, 2),
        "p95_cagr_diff_points": round(float(cagr.quantile(0.95)) * 100, 2),
        "median_drawdown_diff_points": round(float(traded[f"{strategy}_drawdown_diff"].median()) * 100, 2),
    }


def main(source: str, path: Path | None = None) -> int:
    if source == "finsaber":
        path = path or ROOT / "data" / "finsaber" / "prices.csv"
        if not path.exists():
            print("No price file. Run `python src/download_finsaber.py` first.", file=sys.stderr)
            return 1
        raw, repair = repair_finsaber(load_finsaber(path))
        print(f"repair: {repair}")
    elif source == "yahoo":
        path = path or ROOT / "data" / "universe"
        if not (path / "SPY.csv").exists():
            print("No price files. Run `python src/download_universe.py` first.", file=sys.stderr)
            return 1
        raw, repair = load_yahoo(path), {}
    else:
        print("Usage: python src/random_portfolios.py finsaber|yahoo", file=sys.stderr)
        return 1
    RESULTS.mkdir(exist_ok=True)
    CHARTS.mkdir(exist_ok=True)

    prices, last_real = clean(raw)
    vol_30, vol_median = engine.volatility_indicators(prices)
    starts = window_starts(prices)
    print(f"{source}: {len(prices.columns)} tickers, {len(prices)} days, "
          f"{prices.index[0].date()} to {prices.index[-1].date()}")

    rng = np.random.default_rng(SEED)
    rows, original_rows, counts, left_market = [], [], {}, {}
    for start in starts:
        end = start + WINDOW_DAYS
        day, last_day = prices.index[start], prices.index[end - 1]
        year = int(day.year)
        ready = vol_median.iloc[start].notna() & (last_real >= day)
        if source == "finsaber":
            pool = members_on(day)
        else:
            pool = set(universe.RANDOM_DRAW)
            ready &= last_real >= last_day
        eligible = sorted(t for t in prices.columns if t in pool and ready[t])
        if len(eligible) < MIN_TICKERS:
            continue
        counts[year] = len(eligible)
        left_market[year] = int(sum(last_real[t] < last_day for t in eligible))
        original = universe.ORIGINAL_PORTFOLIO
        has_original = all(t in prices.columns and ready[t] for t in original)
        needed = sorted(set(eligible) | (set(original) if has_original else set()))
        signals = {
            s: {t: signals_for(prices, vol_30, vol_median, t, s, start, end) for t in needed}
            for s in STRATEGIES
        }
        for _ in range(PORTFOLIOS_PER_WINDOW):
            tickers = [str(t) for t in rng.choice(eligible, size=POSITIONS, replace=False)]
            weights = dict(zip(tickers, rng.dirichlet(np.full(POSITIONS, 2.0))))
            row = one_case(prices, weights, signals, start, end)
            row.update({"start_year": year, "tickers": " ".join(tickers)})
            rows.append(row)
        if has_original:
            row = one_case(prices, original, signals, start, end)
            row.update({"start_year": year, "tickers": "original portfolio"})
            original_rows.append(row)
        print(f"  {year}: {len(eligible)} tickers, {left_market[year]} left the market in the window", flush=True)

    frame = pd.DataFrame(rows)
    original = pd.DataFrame(original_rows)
    frame.to_csv(RESULTS / f"random_portfolios_{source}.csv", index=False, float_format="%.6f")

    out = {
        "source": source,
        "repair": repair,
        "seed": SEED,
        "window_days": WINDOW_DAYS,
        "first_price_date": str(prices.index[0].date()),
        "last_price_date": str(prices.index[-1].date()),
        "start_years": sorted(counts),
        "tickers_available": counts,
        "tickers_that_left_the_market_in_the_window": left_market,
        "all_cases": {s: summarize(frame, s) for s in STRATEGIES},
        "by_start_year": {
            s: {int(y): summarize(g, s) for y, g in frame.groupby("start_year")} for s in STRATEGIES
        },
        "original_portfolio": {
            int(r["start_year"]): {
                s: {
                    "cagr_diff_points": round(r[f"{s}_cagr_diff"] * 100, 2),
                    "sharpe_diff": round(r[f"{s}_sharpe_diff"], 2),
                    "drawdown_diff_points": round(r[f"{s}_drawdown_diff"] * 100, 2),
                }
                for s in STRATEGIES
            }
            for _, r in original.iterrows()
        },
    }
    (RESULTS / f"random_portfolios_{source}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["all_cases"], indent=2))

    traded = frame[frame["vol_2.5_trims"] > 0]
    diff = traded["vol_2.5_cagr_diff"] * 100
    low, high = diff.quantile(0.005), diff.quantile(0.995)
    marks = [(float(v) * 100, "") for v in original["vol_2.5_cagr_diff"]] if len(original) else []
    plots.histogram(
        diff.clip(low, high), f"Volatility-2.5x against buy-and-hold, {len(traded):,} random cases with a trim",
        "Difference in yearly return (percentage points). Above 0 = the trim rule wins.",
        CHARTS / f"05_random_portfolios_{source}.png",
        markers=marks, marker_label="Original portfolio, each start year",
    )
    plots.scatter(
        traded["largest_position_end"] * 100, diff.clip(low, high),
        "The trim rule against the size of the largest position",
        "Largest position at the end, buy-and-hold (percent of portfolio)",
        "Difference in yearly return (points)", CHARTS / f"06_concentration_{source}.png",
    )
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(main(args[0] if args else "finsaber", Path(args[1]) if len(args) > 1 else None))
