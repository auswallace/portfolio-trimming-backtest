#!/usr/bin/env python3
"""
Investigate validation issues
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

results_dir = '/Users/austinwallace/sandbox/stock_strategies/trim_strat_test/results'

# Load data
with open(f'{results_dir}/trim_50pct_dip_buy_5pct_metadata.json', 'r') as f:
    metadata = json.load(f)

metrics = pd.read_csv(f'{results_dir}/trim_50pct_dip_buy_5pct_metrics.csv')
portfolio = pd.read_csv(f'{results_dir}/trim_50pct_dip_buy_5pct_portfolio_value.csv', index_col=0)
portfolio.index = pd.to_datetime(portfolio.index)

print("=" * 80)
print("INVESTIGATING CAGR CALCULATION")
print("=" * 80)

initial_value = metadata['initial_capital']
final_value = portfolio['Total_Value'].iloc[-1]

print(f"Initial Value: ${initial_value:,.2f}")
print(f"Final Value: ${final_value:,.2f}")
print(f"Total Return: {(final_value/initial_value - 1)*100:.2f}%")

# Calculate time period different ways
start_date = portfolio.index[0]
end_date = portfolio.index[-1]

print(f"\nStart Date: {start_date}")
print(f"End Date: {end_date}")

# Days
total_days = (end_date - start_date).days
print(f"Total Days: {total_days}")

# Years (different methods)
years_365 = total_days / 365
years_365_25 = total_days / 365.25
years_actual = (end_date.year - start_date.year) + (end_date.month - start_date.month) / 12 + (end_date.day - start_date.day) / 365.25

print(f"\nYears (days/365): {years_365:.6f}")
print(f"Years (days/365.25): {years_365_25:.6f}")
print(f"Years (actual): {years_actual:.6f}")

# CAGR calculations
cagr_365 = (final_value / initial_value) ** (1 / years_365) - 1
cagr_365_25 = (final_value / initial_value) ** (1 / years_365_25) - 1
cagr_actual = (final_value / initial_value) ** (1 / years_actual) - 1

print(f"\nCAGR (365 days/year): {cagr_365:.6f} ({cagr_365*100:.2f}%)")
print(f"CAGR (365.25 days/year): {cagr_365_25:.6f} ({cagr_365_25*100:.2f}%)")
print(f"CAGR (actual): {cagr_actual:.6f} ({cagr_actual*100:.2f}%)")

reported_cagr = metrics.iloc[0]['cagr']
print(f"\nReported CAGR: {reported_cagr:.6f} ({reported_cagr*100:.2f}%)")

# Try to reverse engineer which method was used
if abs(cagr_365 - reported_cagr) < 0.0001:
    print("✓ Reported CAGR matches 365 days/year method")
elif abs(cagr_365_25 - reported_cagr) < 0.0001:
    print("✓ Reported CAGR matches 365.25 days/year method")
elif abs(cagr_actual - reported_cagr) < 0.0001:
    print("✓ Reported CAGR matches actual method")
else:
    # Try to find the years value that produces the reported CAGR
    reported_years = np.log(final_value / initial_value) / np.log(1 + reported_cagr)
    print(f"⚠ Reported CAGR implies {reported_years:.6f} years")
    print(f"   That's {reported_years * 365.25:.1f} days")

print("\n" + "=" * 80)
print("INVESTIGATING PORTFOLIO RECONCILIATION")
print("=" * 80)

# Check a few sample dates
sample_dates = [portfolio.index[0], portfolio.index[len(portfolio)//2], portfolio.index[-1]]

for date in sample_dates:
    row = portfolio.loc[date]

    components = row[['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ', 'Cash']]
    calculated_total = components.sum()
    reported_total = row['Total_Value']

    print(f"\nDate: {date.strftime('%Y-%m-%d')}")
    print(f"Component Values:")
    for ticker in ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ', 'Cash']:
        print(f"  {ticker}: ${components[ticker]:,.2f}")
    print(f"Sum of components: ${calculated_total:,.2f}")
    print(f"Reported total: ${reported_total:,.2f}")
    print(f"Difference: ${abs(calculated_total - reported_total):,.2f}")

print("\n" + "=" * 80)
print("UNDERSTANDING THE DATA STRUCTURE")
print("=" * 80)

print("\nFirst row of portfolio:")
print(portfolio.iloc[0])

print("\nLast row of portfolio:")
print(portfolio.iloc[-1])

print("\nColumn names:")
print(portfolio.columns.tolist())

print("\nAre values in SHARES or DOLLARS?")
print("If SHARES, we need price data to calculate dollar values")
print("If DOLLARS, they should sum to Total_Value")

# Check if values look like shares or dollars
first_row = portfolio.iloc[0]
print(f"\nFirst row AAPL value: {first_row['AAPL']:,.2f}")
print(f"Initial capital / 6 tickers = ${initial_value/6:,.2f}")
print("If this is dollars, should be close to 16,666.67")
print("If this is shares, would be very different")

# Check total value at start
print(f"\nReported total at start: ${first_row['Total_Value']:,.2f}")
print(f"Expected: ${initial_value:,.2f}")
