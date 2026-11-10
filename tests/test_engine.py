"""Checks for the engine.

Run:  python tests/test_engine.py     (or: pytest)

The first checks use small invented price tables. The last check uses the
real price files in data/ and reproduces the original headline numbers.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import engine  # noqa: E402


def table(columns: dict) -> pd.DataFrame:
    n = len(next(iter(columns.values())))
    return pd.DataFrame(columns, index=pd.bdate_range("2020-01-01", periods=n), dtype=float)


def test_pro_rata_keeps_the_value():
    # A trim with pro-rata reinvestment moves money. It does not make money.
    prices = table({"A": [10, 20, 20, 20], "B": [10, 10, 10, 10]})
    run = engine.simulate(prices, {"A": 0.5, "B": 0.5}, {"A": [1]}, initial=100, lag=0)
    assert np.allclose(run["value"], [100, 150, 150, 150])
    assert np.allclose(run["cash"], 0)
    assert run["holdings"]["A"].iloc[-1] < run["holdings"]["A"].iloc[0]
    assert run["holdings"]["B"].iloc[-1] > run["holdings"]["B"].iloc[0]


def test_cash_is_recorded_for_each_day():
    # Before the trim there is no cash. The original engine put the final
    # cash balance on all days.
    prices = table({"A": [10, 10, 20, 20], "B": [10, 10, 10, 10]})
    run = engine.simulate(prices, {"A": 0.5, "B": 0.5}, {"A": [2]}, initial=100, reinvest="cash", lag=0)
    assert list(run["cash"]) == [0, 0, 20, 20]
    assert np.allclose(run["value"], [100, 100, 150, 150])


def test_trade_on_the_next_day():
    # With lag=1 the trade uses the price of the day after the signal.
    prices = table({"A": [10, 20, 40, 40], "B": [10, 10, 10, 10]})
    same_day = engine.simulate(prices, {"A": 0.5, "B": 0.5}, {"A": [1]}, initial=100, reinvest="cash", lag=0)
    next_day = engine.simulate(prices, {"A": 0.5, "B": 0.5}, {"A": [1]}, initial=100, reinvest="cash", lag=1)
    assert same_day["trades"][0]["proceeds"] == 20   # 1 share at 20
    assert next_day["trades"][0]["proceeds"] == 40   # 1 share at 40
    assert next_day["trades"][0]["date"] == prices.index[2]


def test_signal_on_the_last_day_makes_no_trade():
    prices = table({"A": [10, 20, 40], "B": [10, 10, 10]})
    run = engine.simulate(prices, {"A": 0.5, "B": 0.5}, {"A": [2]}, initial=100, lag=1)
    assert run["trades"] == []


def test_sharpe_subtracts_the_risk_free_rate():
    rng = np.random.default_rng(0)
    value = pd.Series(100 * np.cumprod(1 + rng.normal(0.0005, 0.01, 1000)))
    zero = engine.metrics(value, 100, risk_free=0.0)
    two = engine.metrics(value, 100, risk_free=0.02)
    assert np.isclose(zero["sharpe"] - two["sharpe"], 0.02 / zero["volatility"])


def test_max_drawdown():
    value = pd.Series([100.0, 120.0, 60.0, 90.0])
    assert np.isclose(engine.metrics(value, 100)["max_drawdown"], -0.5)


def test_threshold_signals():
    # +100% on day 2. The new cost basis is 20 * 1.05 = 21, so 40 is not +100%.
    prices = np.array([10.0, 15.0, 20.0, 40.0, 42.0])
    assert engine.threshold_signals(prices, 1.00) == [2, 4]


def test_volatility_signals_cooldown():
    # The ratio is above the multiplier on all days. One trim each 10 calendar days.
    dates = pd.bdate_range("2020-01-01", periods=30)
    high, median = np.full(30, 3.0), np.full(30, 1.0)
    signals = engine.volatility_signals(dates, high, median, 2.5, warmup=0)
    gaps = [(dates[b] - dates[a]).days for a, b in zip(signals, signals[1:])]
    assert signals[0] == 0 and all(gap >= 10 for gap in gaps)


def test_reproduces_the_original_headline():
    # The original numbers: $688,711 for buy-and-hold, $1,046,173 for Volatility-2.5x.
    weights = {"SPY": 0.30, "QQQ": 0.20, "VOO": 0.10, "AAPL": 0.15, "MSFT": 0.15, "TSLA": 0.10}
    prices = engine.load_prices(ROOT / "data", list(weights), "2015-01-01", "2024-11-05")
    vol_30, vol_median = engine.volatility_indicators(prices)
    signals = {
        t: engine.volatility_signals(prices.index, vol_30[t].to_numpy(), vol_median[t].to_numpy(), 2.5)
        for t in weights
    }
    hold = engine.buy_and_hold(prices, weights)
    run = engine.simulate(prices, weights, signals, lag=0)
    assert round(hold.iloc[-1]) == 688_711
    assert round(run["value"].iloc[-1]) == 1_046_173
    assert signals["TSLA"] == []   # the strategy never trimmed TSLA


def test_repair_cuts_a_reused_symbol():
    # A second company uses the symbol after a gap. The series must stop at the gap.
    import random_portfolios as rp

    first = pd.Series(10.0, index=pd.bdate_range("2020-01-01", periods=30))
    second = pd.Series(5000.0, index=pd.bdate_range("2021-01-01", periods=30))
    good = pd.Series(20.0, index=pd.bdate_range("2020-01-01", periods=300))
    prices = pd.DataFrame({"OLD": pd.concat([first, second]), "GOOD": good})
    fixed, report = rp.repair_finsaber(prices)
    assert fixed["OLD"].dropna().index[-1] == first.index[-1]
    assert len(fixed["GOOD"].dropna()) == 300
    assert report["symbols_cut_short"] == 1 and report["symbols_removed"] == 0


def test_members_on_a_date():
    # TSLA joined the S&P 500 in December 2020. Enron left it in 2001.
    import random_portfolios as rp

    assert "TSLA" not in rp.members_on(pd.Timestamp("2015-01-02"))
    assert "TSLA" in rp.members_on(pd.Timestamp("2021-01-04"))
    assert "ENRNQ" in rp.members_on(pd.Timestamp("2001-01-02"))
    assert "ENRNQ" not in rp.members_on(pd.Timestamp("2003-01-02"))


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"ok    {test.__name__}")
        except AssertionError as err:
            failed += 1
            print(f"FAIL  {test.__name__}  {err}")
    print(f"{len(tests) - failed} of {len(tests)} checks passed")
    sys.exit(1 if failed else 0)
