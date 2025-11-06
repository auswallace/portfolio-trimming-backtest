#!/usr/bin/env python3
"""
Check the CAGR calculation methodology used in the backtest
"""

import pandas as pd
import json

results_dir = '/Users/austinwallace/sandbox/stock_strategies/trim_strat_test/results'

# Load data
with open(f'{results_dir}/trim_50pct_dip_buy_5pct_metadata.json', 'r') as f:
    metadata = json.load(f)

metrics = pd.read_csv(f'{results_dir}/trim_50pct_dip_buy_5pct_metrics.csv')
portfolio = pd.read_csv(f'{results_dir}/trim_50pct_dip_buy_5pct_portfolio_value.csv', index_col=0)
portfolio.index = pd.to_datetime(portfolio.index)

initial_value = metadata['initial_capital']
final_value = portfolio['Total_Value'].iloc[-1]
start_date = pd.to_datetime(metadata['start_date'])
end_date = pd.to_datetime(metadata['end_date'])

print("=" * 80)
print("CAGR CALCULATION ANALYSIS")
print("=" * 80)

print(f"\nMetadata dates:")
print(f"  Start: {start_date}")
print(f"  End: {end_date}")

print(f"\nPortfolio dates:")
print(f"  First entry: {portfolio.index[0]}")
print(f"  Last entry: {portfolio.index[-1]}")

# The metadata dates might be different from actual portfolio dates
metadata_days = (end_date - start_date).days
portfolio_days = (portfolio.index[-1] - portfolio.index[0]).days

print(f"\nDays calculation:")
print(f"  Metadata: {metadata_days} days")
print(f"  Portfolio: {portfolio_days} days")

# Try to reproduce the reported CAGR
reported_cagr = metrics.iloc[0]['cagr']

# Reverse engineer the years used
import numpy as np
years_used = np.log(final_value / initial_value) / np.log(1 + reported_cagr)

print(f"\nReported CAGR: {reported_cagr:.6f}")
print(f"This implies: {years_used:.6f} years")
print(f"Which is: {years_used * 365.25:.1f} days")

# Check if using metadata dates
metadata_years = metadata_days / 365.25
metadata_cagr = (final_value / initial_value) ** (1 / metadata_years) - 1

print(f"\nUsing metadata dates:")
print(f"  Years: {metadata_years:.6f}")
print(f"  CAGR: {metadata_cagr:.6f}")
print(f"  Match: {abs(metadata_cagr - reported_cagr) < 0.0001}")

# The difference suggests the calculation might be using the metadata end_date
# instead of the actual last portfolio date
print(f"\nLikely explanation:")
print(f"  CAGR calculated using metadata end_date (2025-11-05)")
print(f"  But that's the same as portfolio end date")
print(f"  Difference might be in year calculation method")

# Try different year calculation methods
for method, divisor in [('365', 365), ('365.25', 365.25), ('252 trading', 252)]:
    years = metadata_days / divisor
    cagr = (final_value / initial_value) ** (1 / years) - 1
    match = abs(cagr - reported_cagr) < 0.0001
    print(f"\n  Method '{method}':")
    print(f"    Years: {years:.6f}")
    print(f"    CAGR: {cagr:.6f}")
    print(f"    Match: {'✓' if match else '✗'}")

# Maybe it's using calendar years instead of days?
calendar_years = end_date.year - start_date.year
for fractional in [0, 0.25, 0.5, 0.75, 1.0]:
    test_years = calendar_years + fractional
    test_cagr = (final_value / initial_value) ** (1 / test_years) - 1
    if abs(test_cagr - reported_cagr) < 0.001:
        print(f"\n✓ FOUND: {test_years:.2f} years produces matching CAGR")
        print(f"  This is {calendar_years} full years + {fractional} fractional year")
