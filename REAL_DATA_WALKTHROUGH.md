# Running Backtest with Real Data - Complete Walkthrough

## 🎯 Goal
Run the portfolio trimming backtest with **actual historical data** from Yahoo Finance to validate the mock data results.

---

## 📋 Three Options (Pick One)

### **Option 1: Wait & Auto-Run** ⏰ (Easiest)
**When:** Yahoo Finance rate limits clear (usually 24 hours)

**Steps:**
1. Wait until tomorrow (~same time, 6:00 PM)
2. Run:
   ```bash
   cd /Users/austinwallace/sandbox/stock_strategies/trim_strat_test
   python run_backtest_with_dip.py
   ```
3. Wait 5-10 minutes for download and analysis
4. Results automatically saved to `results/`

**Pros:** Fully automated, no manual work
**Cons:** Must wait 24 hours

---

### **Option 2: Manual CSV Download** 📥 (Works Now!)
**When:** Right now (bypasses API rate limits)

#### **Step 1: Download CSVs from Yahoo Finance**

Visit each URL and click "Download":

1. **AAPL:** https://finance.yahoo.com/quote/AAPL/history
   - Set: Jan 1, 2015 → Nov 5, 2024
   - Click "Download" → Saves `AAPL.csv`

2. **MSFT:** https://finance.yahoo.com/quote/MSFT/history
   - Same date range → Download

3. **NVDA:** https://finance.yahoo.com/quote/NVDA/history

4. **TSLA:** https://finance.yahoo.com/quote/TSLA/history

5. **SPY:** https://finance.yahoo.com/quote/SPY/history

6. **QQQ:** https://finance.yahoo.com/quote/QQQ/history

**Time:** ~5 minutes total

#### **Step 2: Move Files to Project**

```bash
cd /Users/austinwallace/sandbox/stock_strategies/trim_strat_test

# Create folder
mkdir manual_data

# Move downloaded CSVs (from ~/Downloads)
mv ~/Downloads/AAPL.csv manual_data/
mv ~/Downloads/MSFT.csv manual_data/
mv ~/Downloads/NVDA.csv manual_data/
mv ~/Downloads/TSLA.csv manual_data/
mv ~/Downloads/SPY.csv manual_data/
mv ~/Downloads/QQQ.csv manual_data/
```

#### **Step 3: Run Backtest**

```bash
python run_backtest_manual_data.py
```

**Output:**
```
Loading AAPL... ✓ (2,519 days)
Loading MSFT... ✓ (2,519 days)
Loading NVDA... ✓ (2,519 days)
Loading TSLA... ✓ (2,519 days)
Loading SPY... ✓ (2,519 days)
Loading QQQ... ✓ (2,519 days)

Running Buy-and-Hold...
Running Trim@+50% (dip-buy-5pct)...
...

TOP 5 STRATEGIES (REAL DATA):
1. Trim@+50% (dip-buy-5pct) - $XXX,XXX
2. ...
```

**Time:** 2-3 minutes

**Pros:** Works immediately, no waiting
**Cons:** Manual CSV download (5 min work)

---

### **Option 3: Alternative Data Source** 🌐 (Advanced)

Use Alpha Vantage, Polygon.io, or other API (requires API key setup).

**Skip this unless you have these APIs already.**

---

## 📊 After Running with Real Data

### **Step 1: Review Results**

Results saved to:
```
results_real_data/real_data_results.csv
```

Open and check:
- Did your 5% dip-buy strategy still win?
- How does CAGR compare to mock data?
- Were there more/fewer trim events?

### **Step 2: Compare Mock vs Real**

Run the comparison script:
```bash
python compare_mock_vs_real.py
```

This shows side-by-side:
```
Metric              Mock Data            Real Data            Difference
--------------------------------------------------------------------------------
final_value         $351,185            $XXX,XXX             $+X,XXX
cagr                11.83%              XX.XX%               +X.XX%
sharpe_ratio        0.88                X.XX                 +X.XX
num_trades          13                  XX                   +X
```

### **Step 3: Validate Real Results** (Optional but Recommended)

Use the validator agent:
```bash
# (Instructions provided after real data run)
```

---

## 🎯 What You'll Learn

### **From Real Data:**

1. **Actual Performance** (2015-2024)
   - Real CAGR over 10 years
   - Actual trim events (not simulated)
   - Real market dips and timing

2. **Strategy Validation**
   - Does dip-buy still outperform?
   - How close was mock data?
   - Which strategy actually won?

3. **Trade Frequency**
   - How often would you have trimmed?
   - How long between dip-buy opportunities?
   - Cash holding periods

4. **Risk Metrics**
   - Real max drawdown (COVID, 2022 bear)
   - Actual volatility
   - True Sharpe/Sortino ratios

---

## ⚠️ Important Notes

### **Expected Differences from Mock Data**

Mock data was **realistic but synthetic**. Real data will differ in:

- **Exact final values** (±10-20% is normal)
- **Number of trim events** (real markets are choppier)
- **Dip frequencies** (real corrections don't follow patterns)
- **Max drawdown** (COVID -35% was extreme)

**BUT:** The **ranking** should be similar (dip-buy should still be top 3)

### **What Won't Change**

- Strategy logic (still trim at +50%, buy at 5% dips)
- Timeframe (still 2015-2024)
- Portfolio composition (same 6 tickers)
- Validation methodology

---

## 🚀 Quick Start (Recommended Path)

**For immediate results:**

1. **Now:** Download 6 CSVs manually (5 minutes)
   - See "Option 2" above

2. **Run:** `python run_backtest_manual_data.py` (2 minutes)

3. **Compare:** `python compare_mock_vs_real.py` (instant)

4. **Review:** `results_real_data/real_data_results.csv`

**Total time: ~10 minutes**

---

**For automated results:**

1. **Wait:** 24 hours from now (~6 PM tomorrow)

2. **Run:** `python run_backtest_with_dip.py`

3. **Done:** Results in `results/`

**Total time: 5 minutes (tomorrow)**

---

## 📁 File Structure After Real Data Run

```
trim_strat_test/
├── manual_data/              # Your CSV files
│   ├── AAPL.csv
│   ├── MSFT.csv
│   ├── NVDA.csv
│   ├── TSLA.csv
│   ├── SPY.csv
│   └── QQQ.csv
├── results_real_data/        # Real backtest results
│   ├── real_data_results.csv
│   └── (50+ strategy files)
├── results/                  # Mock data results (for comparison)
└── trimming_strategy_results_with_dip.csv  # Mock summary
```

---

## 🆘 Troubleshooting

**"Rate limit error"**
- Wait 24 hours and retry
- OR use Option 2 (manual CSV download)

**"File not found: manual_data/AAPL.csv"**
- Check you created `manual_data/` folder
- Check CSV files are in that folder
- Check filenames match exactly: `AAPL.csv` (not `aapl.csv`)

**"No data in date range"**
- When downloading from Yahoo, set dates:
  - Start: 01/01/2015
  - End: 11/05/2024
- Make sure "Historical Data" tab is selected

**"Different number of tickers loaded"**
- Some tickers may not have full 10-year history
- Script will automatically exclude them
- Results will still be valid (just fewer stocks)

---

## ✅ Success Checklist

After running with real data, you should have:

- [ ] Real data results CSV file
- [ ] Comparison showing mock vs real
- [ ] Confirmation that dip-buy strategy still performs well
- [ ] Actual 10-year CAGR for your strategy
- [ ] Real trim events and dip-buy opportunities
- [ ] Validation report (optional)

---

## 📞 Next Steps

After validating with real data:

1. **Review the winning strategy** (likely still dip-buy 5%)
2. **Check if it meets your goals** (CAGR, risk tolerance)
3. **Consider forward-testing** (paper trade for 3-6 months)
4. **Implement gradually** (start with small % of portfolio)

**Remember:** Past performance ≠ future results. This shows what **would have** worked, not what **will** work.

---

**Ready to get started? Pick your option above and let's validate these results!**
