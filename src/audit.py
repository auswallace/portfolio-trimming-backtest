"""The audit: where did the 52% win come from?

Usage:
    python src/audit.py

It reproduces the original headline result, then tests it:
  1. Which positions did the strategy trim?
  2. What did the TSLA weight do?
  3. Does the win stay when one setting changes?
  4. What does the cash bug do to the risk numbers?

Output: results/audit.json and four charts in charts/.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402
import plots  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
CHARTS = ROOT / "charts"

# The original portfolio and period.
WEIGHTS = {"SPY": 0.30, "QQQ": 0.20, "VOO": 0.10, "AAPL": 0.15, "MSFT": 0.15, "TSLA": 0.10}
START, END = "2015-01-01", "2024-11-05"
INITIAL = 100_000
RISK_FREE = 0.02


def vol_signals(prices, multiplier):
    vol_30, vol_median = engine.volatility_indicators(prices)
    return {
        t: engine.volatility_signals(prices.index, vol_30[t].to_numpy(), vol_median[t].to_numpy(), multiplier)
        for t in prices.columns
    }


def end_of(day: str) -> pd.Timestamp:
    """The last moment of a day. The price rows have a time of day in them."""
    return pd.Timestamp(day) + pd.Timedelta(hours=23)


def summary(value, risk_free=0.0):
    m = engine.metrics(value, INITIAL, risk_free)
    return {
        "final_value": round(m["final_value"]),
        "cagr_pct": round(m["cagr"] * 100, 2),
        "sharpe": round(m["sharpe"], 2),
        "max_drawdown_pct": round(m["max_drawdown"] * 100, 1),
    }


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    CHARTS.mkdir(exist_ok=True)
    prices = engine.load_prices(DATA, list(WEIGHTS), START, END)
    out: dict = {"period": [str(prices.index[0].date()), str(prices.index[-1].date())], "days": len(prices)}

    # ---- 1. Reproduce the original result (same-day trades, lag=0).
    hold = engine.buy_and_hold(prices, WEIGHTS, INITIAL)
    signals = vol_signals(prices, 2.5)
    run = engine.simulate(prices, WEIGHTS, signals, INITIAL, lag=0)
    out["reproduce"] = {"buy_and_hold": summary(hold), "volatility_2.5x": summary(run["value"])}
    out["sharpe_with_2pct_risk_free"] = {
        "buy_and_hold": summary(hold, RISK_FREE)["sharpe"],
        "volatility_2.5x": summary(run["value"], RISK_FREE)["sharpe"],
    }

    # ---- 2. Which positions did the strategy trim?
    trades = pd.DataFrame(run["trades"])
    by_ticker = Counter(trades["ticker"])
    out["trims"] = {
        "total": len(trades),
        "by_ticker": {t: int(by_ticker.get(t, 0)) for t in WEIGHTS},
        "by_year": {int(y): int(n) for y, n in trades.groupby(trades["date"].dt.year).size().items()},
    }

    # ---- 3. TSLA weight and share count.
    px = prices[list(WEIGHTS)]
    weight_run = (run["holdings"]["TSLA"] * px["TSLA"]) / run["value"]
    shares_0 = INITIAL * WEIGHTS["TSLA"] / px["TSLA"].iloc[0]
    weight_hold = shares_0 * px["TSLA"] / hold
    checkpoints = ["2020-02-19", "2020-03-23", "2020-06-30", "2021-11-04", str(prices.index[-1].date())]
    out["tsla_weight_pct"] = {
        d: {"strategy": round(float(weight_run.asof(end_of(d))) * 100),
            "buy_and_hold": round(float(weight_hold.asof(end_of(d))) * 100)}
        for d in checkpoints
    }
    out["tsla_weight_pct"]["strategy_peak"] = round(float(weight_run.max()) * 100)
    out["tsla_shares_vs_start"] = round(float(run["holdings"]["TSLA"].iloc[-1] / shares_0), 2)

    # Share of the three index funds at the end.
    funds = ["SPY", "QQQ", "VOO"]
    hold_funds = sum(INITIAL * WEIGHTS[t] / px[t].iloc[0] * px[t].iloc[-1] for t in funds) / hold.iloc[-1]
    run_funds = sum(run["holdings"][t].iloc[-1] * px[t].iloc[-1] for t in funds) / run["value"].iloc[-1]
    out["index_fund_weight_end_pct"] = {
        "strategy": round(float(run_funds) * 100), "buy_and_hold": round(float(hold_funds) * 100)
    }

    # ---- 4. Does the win stay when one setting changes?
    tests = {}
    for multiplier in (1.5, 2.0, 2.5):
        value = engine.simulate(prices, WEIGHTS, vol_signals(prices, multiplier), INITIAL, lag=0)["value"]
        tests[f"multiplier {multiplier}"] = summary(value)
    crash = (prices.index >= "2020-02-20") & (prices.index <= "2020-06-30")
    crash_days = set(np.flatnonzero(crash))
    no_crash = {t: [i for i in days if i not in crash_days] for t, days in signals.items()}
    tests["multiplier 2.5, no trims from Feb to Jun 2020"] = summary(
        engine.simulate(prices, WEIGHTS, no_crash, INITIAL, lag=0)["value"]
    )
    tests["multiplier 2.5, trade on the next day"] = summary(
        engine.simulate(prices, WEIGHTS, signals, INITIAL, lag=1)["value"]
    )
    rest = {t: w for t, w in WEIGHTS.items() if t != "TSLA"}
    no_tsla = {t: w / sum(rest.values()) for t, w in rest.items()}
    prices_5 = prices[list(no_tsla)]
    hold_5 = engine.buy_and_hold(prices_5, no_tsla, INITIAL)
    run_5 = engine.simulate(prices_5, no_tsla, vol_signals(prices_5, 2.5), INITIAL, lag=0)["value"]
    out["without_tsla"] = {"buy_and_hold": summary(hold_5), "volatility_2.5x": summary(run_5)}
    excess = out["reproduce"]["volatility_2.5x"]["final_value"] / out["reproduce"]["buy_and_hold"]["final_value"] - 1
    excess_5 = out["without_tsla"]["volatility_2.5x"]["final_value"] / out["without_tsla"]["buy_and_hold"]["final_value"] - 1
    out["excess_over_buy_and_hold_pct"] = {"with_tsla": round(excess * 100), "without_tsla": round(excess_5 * 100)}
    out["tests"] = tests

    # ---- 5. The cash bug: the original engine added the final cash balance to all days.
    vol_30, _ = engine.volatility_indicators(prices)
    spy_vol = vol_30["SPY"]
    calm = (spy_vol < spy_vol.shift(1).rolling(20).mean()).to_numpy().copy()
    calm[:63] = False
    thr_50 = {t: engine.threshold_signals(prices[t].to_numpy(), 0.50) for t in WEIGHTS}
    thr_100 = {t: engine.threshold_signals(prices[t].to_numpy(), 1.00) for t in WEIGHTS}
    cases = {
        "Trim@+50% (cash)": (thr_50, "cash"),
        "Trim@+100% (cash)": (thr_100, "cash"),
        "Trim@+100% (yield-volatility)": (thr_100, "spy_when_calm"),
        "Volatility-2.5x (yield-volatility)": (signals, "spy_when_calm"),
    }
    out["cash_bug"] = {}
    for name, (sig, mode) in cases.items():
        r = engine.simulate(prices, WEIGHTS, sig, INITIAL, reinvest=mode, lag=0, calm=calm)
        with_bug = r["value"] - r["cash"] + r["cash"].iloc[-1]
        out["cash_bug"][name] = {
            "original_method": summary(with_bug),
            "daily_cash": summary(r["value"]),
            "final_cash_balance": round(float(r["cash"].iloc[-1])),
        }

    (RESULTS / "audit.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))

    # ---- Charts.
    plots.two_lines(
        hold / 1000, run["value"] / 1000, "Buy-and-hold", "Volatility-2.5x",
        "Portfolio value, 2015 to 2024", "Thousand USD", CHARTS / "01_value.png",
    )
    plots.two_lines(
        weight_hold * 100, weight_run * 100, "Buy-and-hold", "Volatility-2.5x",
        "TSLA share of the portfolio", "Percent of portfolio value", CHARTS / "02_tsla_weight.png",
        band=("2020-02-20", "2020-06-30", "Index trims,\nFeb to Jun 2020"),
    )
    plots.bars(
        list(WEIGHTS), [by_ticker.get(t, 0) for t in WEIGHTS],
        "Trims by position: the strategy never trimmed TSLA", "Number of trims", CHARTS / "03_trims.png",
    )
    labels = ["Multiplier 1.5", "Multiplier 2.0", "Multiplier 2.5 (headline)",
              "2.5, no trims Feb to Jun 2020", "2.5, trade on the next day"]
    keys = ["multiplier 1.5", "multiplier 2.0", "multiplier 2.5",
            "multiplier 2.5, no trims from Feb to Jun 2020", "multiplier 2.5, trade on the next day"]
    plots.bars(
        labels, [tests[k]["final_value"] / 1000 for k in keys],
        "Final value when one setting changes", "Thousand USD", CHARTS / "04_tests.png",
        horizontal=True, reference=(out["reproduce"]["buy_and_hold"]["final_value"] / 1000, "Buy-and-hold"),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
