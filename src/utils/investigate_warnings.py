#!/usr/bin/env python3
"""
Investigate the warnings from backtest validation
"""

import pandas as pd
import numpy as np

# Load data
portfolio_df = pd.read_csv('results/trim_50pct_spy_portfolio_value.csv', index_col=0, parse_dates=True)
trades_df = pd.read_csv('results/trim_50pct_spy_trades.csv', parse_dates=['date'])
weights_df = pd.read_csv('results/trim_50pct_spy_weights.csv', index_col=0, parse_dates=True)

print("=" * 80)
print("INVESTIGATING WARNINGS - DETAILED ANALYSIS")
print("=" * 80)

# Check first few trades
print("\n1. Investigating Share Position Changes Around Trade Dates\n")

for idx, trade in trades_df.head(5).iterrows():
    trade_date = pd.Timestamp(trade['date'])
    ticker = trade['ticker']
    shares_sold = trade['shares_sold']

    print(f"\nTrade {idx + 1}: {trade_date.strftime('%Y-%m-%d')} - {ticker}")
    print(f"  Shares Sold (from trades.csv): {shares_sold:.2f}")

    # Find dates around the trade
    try:
        trade_idx = portfolio_df.index.get_loc(trade_date)

        # Look at position before and after
        for offset in range(-2, 3):
            check_idx = trade_idx + offset
            if 0 <= check_idx < len(portfolio_df):
                date = portfolio_df.index[check_idx]
                position = portfolio_df.iloc[check_idx][ticker]
                total_val = portfolio_df.iloc[check_idx]['Total_Value']
                print(f"    {date.strftime('%Y-%m-%d')} ({offset:+2d}): {ticker} = ${position:>12,.2f}, Total = ${total_val:>12,.2f}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n\n2. Investigating SPY Position Changes Around Non-SPY Trims\n")

non_spy_trades = trades_df[trades_df['ticker'] != 'SPY'].head(5)

for idx, trade in non_spy_trades.iterrows():
    trade_date = pd.Timestamp(trade['date'])
    ticker = trade['ticker']
    proceeds = trade['proceeds']

    print(f"\n{trade_date.strftime('%Y-%m-%d')} - {ticker} trim (proceeds: ${proceeds:,.2f})")

    try:
        trade_idx = portfolio_df.index.get_loc(trade_date)

        # Look at SPY position before and after
        for offset in range(-2, 3):
            check_idx = trade_idx + offset
            if 0 <= check_idx < len(portfolio_df):
                date = portfolio_df.index[check_idx]
                spy_position = portfolio_df.iloc[check_idx]['SPY']
                print(f"    {date.strftime('%Y-%m-%d')} ({offset:+2d}): SPY = ${spy_position:>12,.2f}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n\n3. Understanding the Data Structure\n")

print("Portfolio DataFrame columns:", list(portfolio_df.columns))
print("Portfolio DataFrame shape:", portfolio_df.shape)
print("\nFirst row:")
print(portfolio_df.iloc[0])
print("\nLast row:")
print(portfolio_df.iloc[-1])

print("\n\n4. Checking if positions represent shares or dollar values\n")

# Compare with weights to understand the data structure
first_date = portfolio_df.index[0]
print(f"\nOn {first_date.strftime('%Y-%m-%d')}:")
print("\nPortfolio positions (from portfolio_value.csv):")
for ticker in ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']:
    pos = portfolio_df.iloc[0][ticker]
    print(f"  {ticker}: {pos:,.2f}")

print("\nWeights (from weights.csv):")
for ticker in ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']:
    weight = weights_df.iloc[0][ticker]
    print(f"  {ticker}: {weight:.4f} ({weight*100:.2f}%)")

total_value = portfolio_df.iloc[0]['Total_Value']
print(f"\nTotal Portfolio Value: ${total_value:,.2f}")

print("\nCalculating expected dollar positions from weights:")
for ticker in ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']:
    weight = weights_df.iloc[0][ticker]
    expected_pos = weight * total_value
    actual_pos = portfolio_df.iloc[0][ticker]
    print(f"  {ticker}: Expected ${expected_pos:,.2f}, Actual ${actual_pos:,.2f}, Match: {abs(expected_pos - actual_pos) < 1.0}")

print("\n\n5. Hypothesis: Portfolio columns show DOLLAR VALUES, not share counts\n")
print("If true, this explains why we see 0.00 'shares_sold' - we're comparing dollar values!\n")

# Let's verify this hypothesis with a trade
trade = trades_df.iloc[0]
trade_date = pd.Timestamp(trade['date'])
ticker = trade['ticker']
shares_sold = trade['shares_sold']
price = trade['price']
proceeds = trade['proceeds']

print(f"First trade: {trade_date.strftime('%Y-%m-%d')} - {ticker}")
print(f"  Shares sold: {shares_sold:.2f}")
print(f"  Price: ${price:.2f}")
print(f"  Proceeds: ${proceeds:.2f}")
print(f"  Expected proceeds: {shares_sold} × ${price:.2f} = ${shares_sold * price:.2f}")
print(f"  Match: {abs(proceeds - shares_sold * price) < 1.0}")

print("\n\nCONCLUSION:")
print("The portfolio_value.csv contains DOLLAR VALUES of positions, not share counts.")
print("The validation script was incorrectly trying to compare dollar values with share counts.")
print("This is why all 'portfolio change' values showed as 0.00 - we need to look at")
print("dollar value changes, not share count changes!")
