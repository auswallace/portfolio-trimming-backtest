# Manual Data Download Instructions

Since Yahoo Finance API is rate-limited, you can manually download historical data and use it for the backtest.

## Step 1: Download Historical Data from Yahoo Finance Website

For each ticker, visit Yahoo Finance and download CSV files:

### Tickers to Download:
1. AAPL (Apple)
2. MSFT (Microsoft)
3. NVDA (Nvidia)
4. TSLA (Tesla)
5. SPY (S&P 500 ETF)
6. QQQ (Nasdaq-100 ETF)

### How to Download (for each ticker):

1. **Go to:** `https://finance.yahoo.com/quote/AAPL/history`
   (Replace AAPL with each ticker)

2. **Set date range:**
   - Start: January 1, 2015
   - End: Today (November 5, 2024)

3. **Click "Download"** button (top right)
   - Saves as: `AAPL.csv`

4. **Repeat for all 6 tickers**

### Expected Files:
```
AAPL.csv
MSFT.csv
NVDA.csv
TSLA.csv
SPY.csv
QQQ.csv
```

---

## Step 2: Move Files to Project Directory

Place all CSV files in a new folder:

```bash
mkdir -p /Users/austinwallace/sandbox/stock_strategies/trim_strat_test/manual_data/

# Move your downloaded CSVs here:
mv ~/Downloads/AAPL.csv manual_data/
mv ~/Downloads/MSFT.csv manual_data/
mv ~/Downloads/NVDA.csv manual_data/
mv ~/Downloads/TSLA.csv manual_data/
mv ~/Downloads/SPY.csv manual_data/
mv ~/Downloads/QQQ.csv manual_data/
```

---

## Step 3: Run Backtest with Manual Data

Once files are in `manual_data/` folder, run:

```bash
python run_backtest_manual_data.py
```

This will:
- Load your downloaded CSV files
- Run the same backtest with REAL data
- Generate validated results
- Compare to mock data results

---

## Quick Links to Yahoo Finance:

- **AAPL:** https://finance.yahoo.com/quote/AAPL/history
- **MSFT:** https://finance.yahoo.com/quote/MSFT/history
- **NVDA:** https://finance.yahoo.com/quote/NVDA/history
- **TSLA:** https://finance.yahoo.com/quote/TSLA/history
- **SPY:** https://finance.yahoo.com/quote/SPY/history
- **QQQ:** https://finance.yahoo.com/quote/QQQ/history

---

## Time Required:

- **Download time:** ~5 minutes (1 minute per ticker)
- **Backtest run:** ~2 minutes
- **Total:** ~7 minutes

---

## What You'll Get:

After running with real data:
1. ✅ Actual 10-year performance (2015-2024)
2. ✅ Real trim events based on actual prices
3. ✅ Real dip-buy opportunities
4. ✅ Comparison: Real vs Mock results
5. ✅ Full validation reports

**This is the gold standard for validating the strategy!**
