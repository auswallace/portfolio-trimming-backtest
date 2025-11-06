#!/usr/bin/env python
"""
Download data using yfinance_cache (bypasses rate limits)
"""

import yfinance_cache as yfc
import os

TICKERS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']
START_DATE = '2015-01-01'
END_DATE = '2024-11-05'
OUTPUT_DIR = 'manual_data'

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*80)
print("DOWNLOADING DATA WITH yfinance_cache")
print("="*80)

success_count = 0

for i, ticker in enumerate(TICKERS, 1):
    print(f"\n[{i}/{len(TICKERS)}] Downloading {ticker}...", end=' ')

    try:
        data = yfc.download(ticker, start=START_DATE, end=END_DATE, progress=False)

        if len(data) > 0:
            filename = f"{OUTPUT_DIR}/{ticker}.csv"
            data.to_csv(filename)
            print(f"✓ {len(data)} days saved")
            success_count += 1
        else:
            print(f"✗ No data")

    except Exception as e:
        print(f"✗ Error: {str(e)[:50]}")

print("\n" + "="*80)
print(f"Downloaded {success_count}/{len(TICKERS)} tickers successfully")
print("="*80)

if success_count == len(TICKERS):
    print("\n✅ All data downloaded! Ready to run backtest.")
    print("\nNext step:")
    print("  python run_backtest_manual_data.py")
