## Strategy Glossary

Each strategy combines two components: a **trimming trigger** (when to sell) and a **reinvestment mode** (where proceeds go).

---

### Trimming Triggers (When to Sell)

**Buy-and-Hold**
- **What it does**: Never sell. Hold all positions regardless of gains.
- **Example**: TSLA bought at $100 rises to $400 → Do nothing, still hold 100% of position.

**Trim@+50%**
- **What it does**: Sell 20% of a position when it gains 50%.
- **Example**: AAPL bought at $100 rises to $150 → Sell 20% at $150, keep 80%.

**Trim@+100%**
- **What it does**: Sell 20% of a position when it doubles (+100% gain).
- **Example**: MSFT bought at $200 rises to $400 → Sell 20% at $400, keep 80%.

**Trim@+150%**
- **What it does**: Sell 20% of a position when it gains 150% (2.5x).
- **Example**: NVDA bought at $100 rises to $250 → Sell 20% at $250, keep 80%.

**Volatility-2.0x**
- **What it does**: Dynamic threshold based on 2× the stock's 30-day rolling average gain.
- **Example**: If SPY typically gains 5% over 30 days, trim threshold is 10% (2× the average). More volatile = higher threshold.

**Volatility-2.5x**
- **What it does**: Dynamic threshold based on 2.5× the stock's 30-day rolling average gain.
- **Example**: If QQQ typically gains 8% over 30 days, trim threshold is 20% (2.5× the average). Adapts to market conditions.

---

### Reinvestment Modes (Where Proceeds Go)

**pro-rata**
- **What it does**: Immediately reinvest proceeds back into all holdings proportionally.
- **Example**: Sell $10,000 from TSLA → Buy $3,000 SPY, $2,000 QQQ, $1,000 VOO, $1,500 AAPL, $1,500 MSFT, $1,000 TSLA (matching original portfolio allocation).
- **Why**: Maintains exposure to high-growth stocks. Doesn't rotate away from winners.

**drip**
- **What it does**: Gradually reinvest proceeds over 4 weeks (25% per week), pro-rata allocation.
- **Example**: Sell $10,000 from NVDA → Week 1: invest $2,500 pro-rata, Week 2: $2,500, Week 3: $2,500, Week 4: $2,500.
- **Why**: Dollar-cost averaging during volatile periods. Spreads entry timing.

**spy**
- **What it does**: Immediately reinvest all proceeds into SPY (S&P 500 ETF).
- **Example**: Sell $10,000 from AAPL → Buy $10,000 SPY.
- **Why**: Rotate profits from individual stocks to diversified index. Reduces concentration risk.

**dip-buy-5pct**
- **What it does**: Hold proceeds in cash, wait for S&P 500 to drop 5% from recent high, then buy SPY/QQQ (alternating).
- **Example**: Sell $10,000 from MSFT on June 1 → S&P drops 5% on July 15 → Buy $10,000 SPY on July 15.
- **Why**: Attempt to time market entries. Wait for dips before deploying capital.

**yield-volatility**
- **What it does**: Gradually reinvest over 1-8 weeks based on dividend yield and VIX signals. Higher yield + higher VIX = faster reentry.
- **Example**: Sell $10,000 during high volatility (VIX 30) → Reinvest 50% in week 1, 50% in week 2 (fast reentry during fear).
- **Why**: Use market signals to guide reinvestment pace. Buy more aggressively when valuations attractive.

---

### Full Strategy Examples

**Volatility-2.5x (pro-rata)**
- **Trigger**: Trim 20% when position exceeds 2.5× its rolling 30-day average gain.
- **Reinvestment**: Immediately reinvest proceeds across all holdings proportionally.
- **Real scenario**: TSLA gains 60% in a month (2.5× its typical 24% monthly gain) → Trim 20% at peak → Immediately reinvest pro-rata → Maintain exposure to TSLA and other winners.

**Trim@+100% (drip)**
- **Trigger**: Trim 20% when position doubles.
- **Reinvestment**: Gradually reinvest proceeds over 4 weeks (25%/week), pro-rata.
- **Real scenario**: AAPL bought at $150, rises to $300 → Sell 20% → Week 1: invest 25% of proceeds, Week 2: 25%, Week 3: 25%, Week 4: 25% → Dollar-cost average reentry.

**Trim@+150% (spy)**
- **Trigger**: Trim 20% when position gains 150%.
- **Reinvestment**: Immediately rotate all proceeds to SPY.
- **Real scenario**: NVDA bought at $100, rises to $250 → Sell 20% → Immediately buy SPY with all proceeds → Rotate from individual stock to index.

**Volatility-2.0x (yield-volatility)**
- **Trigger**: Trim 20% when position exceeds 2× its rolling average gain.
- **Reinvestment**: Gradually reinvest using yield/VIX signals (1-8 weeks).
- **Real scenario**: QQQ gains 20% (2× its typical 10% gain) during volatile period → Trim 20% → VIX is high (35), so reinvest 40% in week 1, 30% in week 2, 30% in week 3 → Use volatility to guide timing.

**Trim@+150% (dip-buy-5pct)**
- **Trigger**: Trim 20% when position gains 150%.
- **Reinvestment**: Wait for 5% S&P dip, then buy SPY/QQQ alternating.
- **Real scenario**: MSFT bought at $200, rises to $500 → Sell 20% on March 1 → S&P drops 5% on April 10 → Buy SPY with proceeds on April 10 → Wait for dip before redeploying.

---

### Key Takeaway

**Best performers in index-focused portfolio (Phase 3):**
1. **Volatility-2.5x (pro-rata)**: Adapts to market conditions, maintains winner exposure → 26.98% CAGR
2. **Trim@+100% (drip)**: Fixed threshold with gradual reentry → 21.48% CAGR
3. **Buy-and-Hold**: Passive benchmark → 21.69% CAGR

**Worst performers:**
- **Dip-buy strategies**: Cash drag from waiting destroyed returns → 18-20% CAGR
- **SPY rotation**: Moved capital from winners to slower index → 19-21% CAGR
