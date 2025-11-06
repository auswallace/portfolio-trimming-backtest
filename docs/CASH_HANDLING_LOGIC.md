# Cash Handling Logic Documentation

## Overview

This document explains how trim proceeds are handled under each reinvestment mode in the Portfolio Trimming Strategy Backtest.

**Last Updated**: 2025-11-06
**Backtest Period**: 2015-01-02 to 2024-11-04 (2,477 trading days)

---

## Reinvestment Modes

### 1. **Pro-Rata Reinvestment** (`pro_rata`)

**Logic**: Trim proceeds are immediately reinvested proportionally across all holdings based on current portfolio weights.

**Implementation**:
```python
total_value = sum(holdings[ticker] * price[ticker] for ticker in tickers)
for ticker in tickers:
    weight = (holdings[ticker] * price[ticker]) / total_value
    holdings[ticker] += (proceeds * weight) / price[ticker]
```

**Cash Held**: $0 (always fully invested)

**Characteristics**:
- Maintains exposure to winners
- No market timing element
- No cash drag

**Performance**: Generally best for threshold-based strategies (Trim@+100%/+150%)

---

### 2. **SPY Reinvestment** (`spy`)

**Logic**: Trim proceeds are immediately reinvested into SPY (S&P 500 ETF).

**Implementation**:
```python
holdings['SPY'] += proceeds / price['SPY']
```

**Cash Held**: $0 (always fully invested)

**Characteristics**:
- Rotates profits from individual stocks to index
- Reduces concentration risk
- May underperform if trimmed stock continues rising

**Performance**: Moderate performance, reduces volatility

---

### 3. **Cash Hold** (`cash`)

**Logic**: Trim proceeds are held in cash indefinitely. No reinvestment occurs.

**Implementation**:
```python
cash += proceeds
```

**Cash Held**: Accumulates over time (can reach 30-40% of portfolio)

**Characteristics**:
- Extreme defensive positioning
- Significant opportunity cost in bull markets
- Cash earns 0% (no interest modeled)

**Performance**: Poorest performance across all strategies due to cash drag

**Use Case**: Only viable in bear markets or high-inflation environments with positive real interest rates

---

### 4. **Dip-Buy 5% Strategy** (`dip_buy_5pct`)

**Logic**: Trim proceeds are held in cash until SPY drops 5% from its recent high. Then proceeds are used to buy SPY or QQQ alternately.

**Implementation**:
```python
# Track SPY recent high
spy_recent_high = max(spy_recent_high, current_spy_price)

# Calculate current drop
current_drop = (spy_recent_high - current_spy_price) / spy_recent_high

# Buy on dip
if current_drop >= 0.05 and cash_waiting > 0:
    next_ticker = buy_queue[buy_index]  # Alternate SPY/QQQ
    holdings[next_ticker] += cash_waiting / price[next_ticker]
    cash_waiting = 0
    buy_index = (buy_index + 1) % 2
    spy_recent_high = current_spy_price  # Reset high after buy
```

**Cash Held**: Variable (accumulates between dips, then deploys)

**Dip-Buy Frequency**: 6-11 dips executed over 10 years (depending on trim frequency)

**Characteristics**:
- Market timing strategy
- Waits for 5% corrections
- Alternates between SPY and QQQ for diversification

**Performance**: Underperforms immediate reinvestment
- Opportunity cost: Cash sits idle waiting for dips in bull market
- Typical result: -1% to -3% CAGR vs instant reinvestment

**Historical Dip Buys** (Threshold strategies):
- Trim@+50%: 7 dip buys
- Trim@+100%: 9 dip buys
- Trim@+150%: 6 dip buys

---

### 5. **Drip Reinvestment** (`drip`)

**Logic**: Trim proceeds are reinvested gradually over 4 weeks (25% per week) OR immediately when volatility normalizes.

**Implementation**:
```python
# Check if volatility normalized
vol_30d = volatility['SPY'][-30:].std()
vol_3mo_avg = volatility['SPY'][-63:].std().mean()
volatility_normalized = vol_30d < 1.2 * vol_3mo_avg

# Reinvest schedule
if volatility_normalized:
    amount_to_reinvest = drip_cash  # Deploy all cash
else:
    if day % 5 == 0:  # Every week (5 trading days)
        amount_to_reinvest = drip_cash * 0.25  # 25% per week

# Reinvest pro-rata
total_value = sum(holdings[t] * price[t] for t in tickers)
for t in tickers:
    weight = (holdings[t] * price[t]) / total_value
    holdings[t] += (amount_to_reinvest * weight) / price[t]

drip_cash -= amount_to_reinvest
```

**Cash Held**: Temporarily elevated during drip period, then returns to $0

**Characteristics**:
- Dollar-cost averaging effect
- Avoids deploying all cash at potential local peak
- Accelerates reinvestment when volatility drops

**Performance**:
- **Best performer with volatility-based strategies!**
- Volatility-2.5x (drip): 26.24% CAGR (vs 21.69% B&H)
- Smooth gradual deployment reduces timing risk

---

### 6. **Yield/Volatility-Based Reentry** (`yield_volatility`)

**Logic**: Trim proceeds are held in "Treasury cash" (simulating T-bill investment) and gradually reinvested when volatility normalizes (20% per day).

**Original Intent**: Wait until SPY earnings yield > T-bill yield + 1.5%
**Actual Implementation**: Simplified to volatility normalization only (earnings yield data not available)

**Implementation**:
```python
# Check if volatility normalized
vol_30d = volatility['SPY'][-30:].std()
vol_20d_avg = volatility['SPY'][-20:].std().mean()
volatility_normalized = vol_30d < vol_20d_avg

# Gradual reentry (20% per day to avoid spikes)
if volatility_normalized and treasury_cash > 100:
    amount_to_reinvest = treasury_cash * 0.20
    holdings['SPY'] += amount_to_reinvest / price['SPY']
    treasury_cash -= amount_to_reinvest
```

**Cash Held**: Can accumulate significantly, deploys gradually when volatility drops

**Characteristics**:
- Defensive during high volatility
- Gradual reentry prevents massive portfolio swings
- Implicitly earns T-bill rate (not modeled, assumed 0%)

**Performance**:
- Moderate to poor (due to opportunity cost)
- Fixed version (gradual 20%/day reentry) prevents metric explosions
- Original version had bugs (one-day 17,000%+ returns from full cash dumps)

**Fixes Applied**:
- Gradual reentry (20% per day) instead of instant deployment
- Minimum cash threshold ($100) to avoid tiny reinvestments

---

## Performance Summary by Reinvestment Mode

| Mode | Best CAGR | Worst CAGR | Avg Cash Held | Best Use Case |
|------|-----------|------------|---------------|---------------|
| **pro_rata** | 26.98% (Vol-2.5x) | 16.35% (Trim@+50%) | $0 | Threshold strategies, maintain winner exposure |
| **spy** | 20.92% (Trim@+150%) | 14.22% (Vol-1.5x) | $0 | Rotation to index, reduce concentration |
| **cash** | 19.47% (Trim@+150%) | 4.54% (Vol-1.5x) | $100k-$170k | Bear markets only (not viable in bull) |
| **dip_buy_5pct** | 20.98% (Trim@+150%) | 14.14% (Vol-1.5x) | Variable | Market timing, but underperforms |
| **drip** | 26.24% (Vol-2.5x) | 18.89% (Vol-1.5x) | Temporary | Volatility strategies, DCA effect |
| **yield_volatility** | 20.89% (Trim@+150%) | 12.14% (Vol-1.5x) | Variable | Volatility normalization, defensive |

**Buy-and-Hold Baseline**: 21.69% CAGR, $688,711 final value

---

## Key Insights

### 1. **Pro-Rata Dominates for High-Performing Strategies**
When a strategy works well (Volatility-2.5x), pro-rata reinvestment performs best because it maintains exposure to the best-performing assets.

### 2. **Cash Is Expensive in Bull Markets**
Every strategy with prolonged cash holding (cash, dip_buy_5pct, yield_volatility) underperforms immediate reinvestment by 1-5% CAGR.

### 3. **Drip Shines with High-Frequency Strategies**
Volatility-based strategies trim frequently. Drip reinvestment smooths this by deploying gradually, reducing timing risk.

### 4. **Dip-Buying Sounds Smart, Performs Poorly**
Despite intuitive appeal, waiting for 5% dips costs 1-2% CAGR vs instant reinvestment. Opportunity cost > timing benefit in 2015-2024 bull run.

### 5. **Market Environment Matters**
All results are from a 10-year bull market (2015-2024). Cash and dip-buying strategies might outperform in:
- Bear markets
- High-volatility sideways markets
- High-inflation environments (if cash earns real interest)

---

## Cost Basis Reset Logic

**Applies to**: Threshold-based strategies only (not momentum or volatility)

**Logic**: After trimming, cost basis is reset to current price + 5%

```python
if trim_triggered:
    # Sell 20% of position
    proceeds = holdings[ticker] * 0.20 * current_price

    # Reset cost basis
    cost_basis[ticker] = current_price * 1.05
```

**Rationale**:
- Allows position to re-trigger same threshold
- Without reset, a +50% threshold would only trigger once
- 5% buffer prevents immediate re-trigger on minor price fluctuation

**Example**:
- Buy at $100
- Trim at +50% ($150)
- Cost basis reset to $150 × 1.05 = $157.50
- Next trim triggers at $157.50 × 1.50 = $236.25

---

## Transaction Costs & Taxes

**Current Implementation**: **NOT MODELED**

**Impact if Added**:
- Transaction costs (0.1% per trade): -0.5% to -2% CAGR (depending on trim frequency)
- Capital gains tax (20% long-term): -3% to -8% CAGR for trimming strategies
- Buy-and-hold: No ongoing capital gains until final sale

**Recommendation**: Add toggleable cost/tax parameters before publication (see UPDATE 3 goals).

---

## Edge Cases & Handling

### Zero Holdings
```python
if holdings[ticker] <= 0:
    continue  # Skip trimming logic
```

### Division by Zero
```python
weight = (holdings[t] * price[t]) / total_value if total_value > 0 else 1.0 / len(tickers)
```

### Extreme Returns (>50% daily)
```python
returns_capped = returns.clip(-0.5, 0.5)  # Cap at ±50% for metric calculation
```

### Volatility Strategy Cooldown
```python
if ticker in last_trim_dates:
    days_since_trim = (current_date - last_trim_dates[ticker]).days
    if days_since_trim < 10:  # 10-day cooldown
        return False  # Don't trim yet
```

---

## Code References

**Main backtest engine**: `src/backtest/run_backtest_index_focus.py`
- Cash handling: Lines 489-503
- Drip reinvestment: Lines 368-387
- Dip-buy logic: Lines 342-365
- Yield/volatility reentry: Lines 390-403

**Helper functions**:
- `run_single_strategy()`: Lines 344-543 (orchestrates reinvestment logic)
- `calculate_metrics()`: Lines 305-360 (metrics calculation)

---

## Future Enhancements

1. **Interest on cash**: Model T-bill rates for cash/treasury holdings
2. **Transaction costs**: Add 0.05-0.10% per trade
3. **Tax modeling**: 15-20% capital gains on trim proceeds
4. **Dynamic drip schedules**: Adjust drip rate based on market conditions
5. **Yield-based reentry**: Implement actual SPY earnings yield comparison
6. **Partial SPY reinvestment**: Instead of 100% SPY, allow blended reinvestment (e.g., 50% SPY + 50% pro-rata)

---

**End of Documentation**
