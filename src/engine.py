"""Portfolio trimming engine.

A small engine for the audit and for the random-portfolio test.

A trim sells a fixed part of one position. The proceeds go back into the
portfolio in one of three ways:

  pro_rata        buy all positions in proportion to their current value
  cash            hold the cash
  spy_when_calm   hold the cash, then move 20% of it each day into SPY
                  when SPY volatility is below its 20-day average

Two settings control how honest the test is:

  lag=0   trade at the close of the signal day (the original method)
  lag=1   trade at the close of the next day (no same-day information)

The cash balance is recorded for each day. The original engine added the
final cash balance to all days, which made the risk numbers of the cash
modes wrong.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

TRADING_DAYS = 252


# ------------------------------------------------------------------ data
def load_prices(data_dir, tickers, start=None, end=None) -> pd.DataFrame:
    """Load adjusted close prices, one column for each ticker."""
    columns = {}
    for ticker in tickers:
        df = pd.read_csv(Path(data_dir) / f"{ticker}.csv")
        dates = pd.to_datetime(df["Date"], utc=True).dt.tz_localize(None)
        columns[ticker] = pd.Series(df["Close"].to_numpy(), index=dates)
    prices = pd.DataFrame(columns).sort_index()
    if start is not None:
        prices = prices[prices.index >= pd.Timestamp(start)]
    if end is not None:
        prices = prices[prices.index <= pd.Timestamp(end)]
    return prices.ffill().dropna()


def volatility_indicators(prices: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (30-day volatility, 1-year median of 1-year volatility), annualized."""
    returns = prices.pct_change()
    vol_30 = returns.rolling(30).std() * np.sqrt(TRADING_DAYS)
    vol_median = returns.rolling(252).std().rolling(252).median() * np.sqrt(TRADING_DAYS)
    return vol_30, vol_median


# --------------------------------------------------------------- metrics
def metrics(value: pd.Series, initial: float, risk_free: float = 0.0) -> dict:
    """Performance numbers for a daily portfolio value series.

    The Sharpe ratio subtracts `risk_free` (an annual rate). The original
    engine reported a 2% rate but used 0%.
    """
    returns = value.pct_change().dropna()
    years = len(value) / TRADING_DAYS
    cagr = (value.iloc[-1] / initial) ** (1 / years) - 1
    vol = returns.std() * np.sqrt(TRADING_DAYS)
    sharpe = (returns.mean() * TRADING_DAYS - risk_free) / vol if vol > 0 else 0.0
    drawdown = value / value.cummax() - 1
    return {
        "final_value": float(value.iloc[-1]),
        "cagr": float(cagr),
        "volatility": float(vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown.min()),
    }


# ---------------------------------------------------------- trim signals
def volatility_signals(
    dates,
    vol_30: np.ndarray,
    vol_median: np.ndarray,
    multiplier: float,
    start: int = 0,
    end: int | None = None,
    warmup: int = 252,
    hysteresis: float = 0.9,
    cooldown_days: int = 10,
) -> list[int]:
    """Signal days for one ticker: volatility above `multiplier` x its median.

    The signal starts when the ratio goes above `multiplier` and stops when
    it goes below `multiplier * hysteresis`. While the signal is active, one
    trim occurs each `cooldown_days` calendar days.
    """
    end = len(dates) if end is None else end
    active = False
    last = None
    signals = []
    for i in range(start + warmup, end):
        a, b = vol_30[i], vol_median[i]
        if not (a == a and b == b and b > 0):  # NaN check
            continue
        ratio = a / b
        if not active and ratio > multiplier:
            active = True
        elif active and ratio < multiplier * hysteresis:
            active = False
        if not active:
            continue
        if last is not None and (dates[i] - dates[last]).days < cooldown_days:
            continue
        signals.append(i)
        last = i
    return signals


def threshold_signals(
    prices: np.ndarray, threshold: float, start: int = 0, end: int | None = None
) -> list[int]:
    """Signal days for one ticker: gain on the cost basis is `threshold` or more.

    After a trim, the cost basis becomes the trim price plus 5% (as in the
    original engine).
    """
    end = len(prices) if end is None else end
    basis = prices[start]
    signals = []
    for i in range(start, end):
        if (prices[i] - basis) / basis >= threshold:
            signals.append(i)
            basis = prices[i] * 1.05
    return signals


# ------------------------------------------------------------ simulation
def simulate(
    prices: pd.DataFrame,
    weights: dict[str, float],
    signals: dict[str, list[int]],
    initial: float = 100_000,
    trim_pct: float = 0.20,
    reinvest: str = "pro_rata",
    lag: int = 1,
    start: int = 0,
    end: int | None = None,
    calm: np.ndarray | None = None,
) -> dict:
    """Run one strategy on one portfolio.

    `signals` maps a ticker to its signal days (row numbers of `prices`).
    `calm` is a boolean array for the spy_when_calm mode.
    Returns the daily value, holdings, cash and the list of trades.
    """
    tickers = list(weights)
    px = prices[tickers].to_numpy()
    end = len(px) if end is None else end
    n = end - start
    holdings = np.array([initial * weights[t] / px[start, k] for k, t in enumerate(tickers)])
    cash = 0.0

    by_day: dict[int, list[int]] = {}
    for k, ticker in enumerate(tickers):
        for i in signals.get(ticker, []):
            day = i + lag
            if start <= day < end:
                by_day.setdefault(day, []).append(k)

    held = np.empty((n, len(tickers)))
    cash_series = np.zeros(n)
    trades = []
    spy = tickers.index("SPY") if "SPY" in tickers else None
    daily = reinvest == "spy_when_calm"
    days = range(start, end) if daily else sorted(by_day)
    filled = start

    for day in days:
        held[filled - start: day - start] = holdings
        cash_series[filled - start: day - start] = cash
        filled = day
        if daily and cash > 100 and calm is not None and calm[day] and spy is not None:
            amount = cash * 0.20
            holdings[spy] += amount / px[day, spy]
            cash -= amount
        for k in sorted(by_day.get(day, [])):
            shares = holdings[k] * trim_pct
            proceeds = shares * px[day, k]
            holdings[k] -= shares
            trades.append({"date": prices.index[day], "ticker": tickers[k], "proceeds": proceeds})
            if reinvest == "pro_rata":
                values = holdings * px[day]
                holdings += proceeds * (values / values.sum()) / px[day]
            else:
                cash += proceeds
    held[filled - start:] = holdings
    cash_series[filled - start:] = cash

    index = prices.index[start:end]
    value = (held * px[start:end]).sum(axis=1) + cash_series
    return {
        "value": pd.Series(value, index=index),
        "holdings": pd.DataFrame(held, index=index, columns=tickers),
        "cash": pd.Series(cash_series, index=index),
        "trades": trades,
    }


def buy_and_hold(prices, weights, initial=100_000, start=0, end=None) -> pd.Series:
    """Daily value of a portfolio with no trades."""
    return simulate(prices, weights, {}, initial=initial, start=start, end=end)["value"]
