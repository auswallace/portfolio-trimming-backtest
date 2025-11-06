#!/usr/bin/env python
"""
Download historical data one ticker at a time with long delays
This avoids rate limiting by being very conservative
"""

import yfinance as yf
import pandas as pd
import time
import os

TICKERS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']
START_DATE = '2015-01-01'
END_DATE = '2024-11-05'
OUTPUT_DIR = 'manual_data'

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*80)
print("DOWNLOADING HISTORICAL DATA (SLOW & CAREFUL)")
print("="*80)
print(f"\nThis will take ~10 minutes to avoid rate limits")
print(f"Downloading {len(TICKERS)} tickers with 2-minute delays\n")

for i, ticker in enumerate(TICKERS, 1):
    print(f"\n[{i}/{len(TICKERS)}] Downloading {ticker}...")

    try:
        # Download data
        data = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            progress=False,
            auto_adjust=True
        )

        if not data.empty:
            # Save to CSV
            filename = f"{OUTPUT_DIR}/{ticker}.csv"
            data.to_csv(filename)

            print(f"  ✓ Success: {len(data)} days saved to {filename}")
            print(f"  Price range: ${data['Close'].iloc[0]:.2f} → ${data['Close'].iloc[-1]:.2f}")
        else:
            print(f"  ✗ No data received")

    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")

    # Wait 2 minutes between tickers (except after last one)
    if i < len(TICKERS):
        print(f"\n  ⏳ Waiting 2 minutes before next ticker...")
        print(f"     (This avoids rate limiting)")
        time.sleep(120)  # 2 minutes

print("\n" + "="*80)
print("DOWNLOAD COMPLETE")
print("="*80)

# Check what we got
csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')]
print(f"\n✓ Downloaded {len(csv_files)} files:")
for f in sorted(csv_files):
    print(f"  - {f}")

if len(csv_files) == len(TICKERS):
    print(f"\n✅ All {len(TICKERS)} tickers downloaded successfully!")
    print(f"\nNext step:")
    print(f"  python run_backtest_manual_data.py")
else:
    print(f"\n⚠️  Only got {len(csv_files)}/{len(TICKERS)} tickers")
    print(f"Missing: {set(TICKERS) - {f.replace('.csv', '') for f in csv_files}}")
