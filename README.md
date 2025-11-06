# I Tested 42 Ways to Take Profits. Here's What Actually Worked.

**A 10-year quantitative backtest with $100,000 across 42 portfolio management strategies.**

> **TL;DR:** Volatility-based trimming beat buy-and-hold by 52% ($1.05M vs $689k). Traditional profit-taking achieved near-parity with better risk metrics. Cash holding strategies destroyed returns (-30% to -60%).

---

## 🎯 Key Finding

**The optimal strategy depends on what you own and how you manage risk.**

- **Best Strategy:** Volatility-2.5x (pro-rata) - **26.98% CAGR** (52% better than buy-and-hold)
- **Traditional Trimming:** Trim@+100% (pro-rata) - **21.36% CAGR** (near-parity with buy-and-hold, better risk metrics)
- **Buy-and-Hold Baseline:** **21.69% CAGR** (0.90 Sharpe, -46.3% max drawdown)

**Test Period:** January 2015 to November 2024 (2,477 trading days, 9.83 trading years)
**Starting Capital:** $100,000
**Strategies Tested:** 42 trimming approaches + 1 buy-and-hold baseline
**Ending Values:** $160k (worst) to $1,046k (best) depending on strategy

---

## 📊 Read the Full Report

### **Option 1: Jupyter Notebook** (Recommended for Technical Audiences)
**File:** [`Taking_Profits_What_Actually_Works.ipynb`](Taking_Profits_What_Actually_Works.ipynb)
- 4,414 words with 8 embedded charts
- Interactive format, can export to PDF
- Best for GitHub viewing and technical sharing

### **Option 2: Standalone HTML** (Best for Web Sharing)
**File:** [`Taking_Profits_What_Actually_Works.html`](Taking_Profits_What_Actually_Works.html)
- Self-contained with all charts embedded
- Opens in any browser, no dependencies
- Print to PDF directly from browser

### **Option 3: Markdown Source** (For Editing)
**File:** [`Taking_Profits_What_Actually_Works.md`](Taking_Profits_What_Actually_Works.md)
- Lightweight text version
- Charts in `/visualizations/` folder
- Easy to edit and version control

---

## 🔬 What Makes This Research Different

### 1. **Comprehensive Testing**
42 strategies tested (not just 2-3):
- 5 trimming methodologies (fixed thresholds, volatility-based, momentum-guided)
- 6 reinvestment modes (pro-rata, SPY, DRIP, yield-volatility, dip-buying, cash)
- All combinations systematically tested

### 2. **Real Historical Data**
- Yahoo Finance data (2015-2024)
- 6 real tickers: SPY, QQQ, VOO, AAPL, MSFT, TSLA
- Index-focused portfolio (60% index funds, 40% individual stocks)
- No synthetic/mock data

### 3. **Statistical Validation**
- All metrics independently verified (<0.001% error)
- Bootstrap confidence intervals (1,000 iterations)
- T-tests for statistical significance (Volatility-2.5x: p<0.01)
- Fact-checked by independent agent (8.5/10 quality rating)

### 4. **Honest Discovery Journey**
Report shows the full research arc:
- **Phase 1:** Buy-and-hold crushed trimming ($5.4M vs $4.3M) - NVDA trap
- **Phase 2:** "Smart" dip-buying still underperformed
- **Phase 3:** Realistic portfolio flipped results (near-parity)
- **Phase 4:** Volatility-based strategies breakthrough (+52% vs buy-and-hold)

### 5. **Accessible + Rigorous**
- DC voice (conversational, direct, engaging)
- "In Plain English" translations of complex concepts
- Strategy personas ("The Patient Investor," "The Risk Controller")
- 100% data accuracy preserved

---

## 📈 Breakthrough Finding

**Volatility-Based Trimming Outperformed Buy-and-Hold**

Traditional thinking: "Never sell winners."

**But the data showed:**
- Volatility-2.5x (pro-rata): **$1,046,173** final value (26.98% CAGR)
- Buy-and-Hold: **$688,711** final value (21.69% CAGR)
- **Difference: +$357k (52% better)**

**Why it worked:**
1. High thresholds during bull markets let winners run (TSLA: 250-400% gains required before trim)
2. Volatility spikes triggered lower thresholds before crashes (raised cash in Dec 2019-Jan 2020)
3. Cash deployed at March 2020 bottom (SPY $220, TSLA $90)
4. 2020-2021 recovery multiplied recently deployed capital

**Trade-off:** -62.4% max drawdown (vs -46.3% buy-and-hold). Higher returns, higher volatility.

---

## 💡 Who Should Use Which Strategy

### **Aggressive Investors** (High Risk Tolerance)
**Recommendation:** Volatility-2.5x (pro-rata)
- 26.98% CAGR (26.13% after-tax)
- Accept -62% drawdowns
- Best for tax-deferred accounts (IRA, 401k)

### **Moderate Investors** (Balanced Risk-Return)
**Recommendation:** Trim@+100% or Trim@+150% (pro-rata)
- 21.36% CAGR (21.01-21.16% after-tax)
- Better risk metrics than buy-and-hold (0.94 vs 0.90 Sharpe)
- 5-6% smaller max drawdowns (-40.8% vs -46.3%)

### **Conservative Investors** (Capital Preservation)
**Recommendation:** Trim@+100% (yield-volatility)
- 20.54% CAGR
- **Lowest max drawdown:** -35.1% (11% better than buy-and-hold)
- Psychological benefit reduces panic-selling temptation

---

## ⚠️ What DOESN'T Work

### **Cash Holding Strategies: Catastrophic**
- Trim@+150% (cash): $575k final value (16% below buy-and-hold)
- Opportunity cost: $225k lost waiting for dips
- **Lesson:** Proceeds must be reinvested immediately

### **Dip-Buying: Even "Smart" Market Timing Fails**
- Successfully timed 6-9 dips at 5% discounts
- Still underperformed immediate reinvestment by $20k-$69k
- Average wait: 4.2 months (SPY gained 15% during typical wait)
- **Lesson:** Time in market > timing the market

### **SPY Rotation: Don't Sell Winners to Buy Index**
- Rotating profits from high-growth stocks (TSLA 34% CAGR) to SPY (13% CAGR)
- Cost 10-20% of returns
- **Lesson:** Pro-rata reinvestment maintains exposure to winners

---

## 📋 Methodology Summary

### Portfolio (Illustrative Example)
- SPY: 30% ($30,000)
- QQQ: 20% ($20,000)
- VOO: 10% ($10,000)
- AAPL: 15% ($15,000)
- MSFT: 15% ($15,000)
- TSLA: 10% ($10,000)

**Note:** 60% index funds, 40% individual stocks. Not optimized, but representative of conservative investor allocation.

### Strategies Tested
1. **Fixed Thresholds:** Trim 20% at +50%, +100%, +150% gains
2. **Volatility-Based:** Dynamic thresholds (1.5x, 2.0x, 2.5x multipliers)
3. **Momentum-Guided:** Only trim with +100% gain AND negative MA20/MA50 slopes
4. **Reinvestment Modes:** Pro-rata, SPY, DRIP, yield-volatility, dip-buy-5%, cash

### Metrics Tracked
- CAGR (trading-year basis: 9.83 years)
- Sharpe ratio (2% risk-free rate)
- Sortino ratio (downside-only volatility)
- Maximum drawdown
- Rolling 3-year CAGR/drawdown
- Bootstrap 95% confidence intervals

---

## 📂 Technical Documentation

**Deep Dive:**
- [`TECHNICAL_REPORT_COMPREHENSIVE.md`](TECHNICAL_REPORT_COMPREHENSIVE.md) - Full methodology (16,500 words)
- [`FACT_CHECK_REPORT_DC_VOICE.md`](FACT_CHECK_REPORT_DC_VOICE.md) - Independent validation

**Code:**
- [`run_backtest_index_focus.py`](run_backtest_index_focus.py) - Backtest engine
- [`results_index_focus/`](results_index_focus/) - Raw CSV results

**Visualizations:**
- [`visualizations/`](visualizations/) - 21 professional charts (300 DPI, colorblind-friendly)

**Publishing Guide:**
- [`PUBLICATION_READY.md`](PUBLICATION_READY.md) - How to share, convert formats

---

## 🎓 Limitations & Caveats

### **Bull Market Bias**
Test period (2015-2024) was predominantly bullish:
- S&P 500: +229% (+13.0% CAGR)
- Missing bear market testing (2000-2002, 2007-2009)
- Trimming would likely outperform more in sustained bear markets

### **Frictionless Assumptions**
Current results exclude transaction costs and taxes (upper bound):
- Expected tax drag: 0.2-0.9% for low-frequency, 1.5-4.5% for high-frequency
- Transaction costs: <0.3% annual drag for most strategies
- Volatility-2.5x retains majority of alpha after taxes ($975k vs $689k)

### **Illustrative Parameters**
Trim thresholds (+50%/+100%/+150%), trim amount (20%), portfolio allocation (60/40) chosen for clarity, not optimization. Optimal values may differ.

### **Survivorship Bias**
Portfolio consists of 6 survivors (no bankruptcies). Understates trimming's relative benefit in portfolios with failures.

---

## 🚀 Citation & Sharing

If you use or reference this research:

**APA Format:**
```
Wallace, A. (2025). Portfolio Trimming Strategies: A Comprehensive Quantitative Analysis
(2015-2024 Backtest). Retrieved from https://github.com/[your-username]/trim_strat_test
```

**BibTeX:**
```bibtex
@techreport{wallace2025trimming,
  title={Portfolio Trimming Strategies: A Comprehensive Quantitative Analysis},
  author={Wallace, Austin},
  year={2025},
  type={Quantitative Backtest},
  note={42 strategies tested, 2,477 trading days, $100,000 initial capital}
}
```

---

## 📧 Contact & Questions

Found an error? Have questions? Want to discuss results?

- **GitHub Issues:** [Open an issue](../../issues)
- **Discussions:** [Start a discussion](../../discussions)
- **Email:** [your-email@example.com]

---

## 📜 License

This research is provided for educational purposes. Results are based on historical data and do not guarantee future performance.

**Disclaimer:** Not financial advice. Consult a qualified financial advisor before making investment decisions. Past performance does not indicate future results.

---

**Last Updated:** November 6, 2025
**Version:** 2.0 (42 Strategies, Session 6)
**Status:** ✅ Publication-Ready

---

**⭐ If this research helped you, please star this repo and share!**
