#!/usr/bin/env python3
"""
Verify CAGR using trading days method
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
total_return = (final_value / initial_value) - 1

print("=" * 80)
print("VERIFYING CAGR CALCULATION (TRADING DAYS METHOD)")
print("=" * 80)

print(f"\nInitial Value: ${initial_value:,.2f}")
print(f"Final Value: ${final_value:,.2f}")
print(f"Total Return: {total_return:.4f} ({total_return*100:.2f}%)")

# Method used in backtest: trading days (252 per year)
num_portfolio_rows = len(portfolio)
years_trading = num_portfolio_rows / 252

print(f"\nNumber of portfolio rows: {num_portfolio_rows}")
print(f"Years (trading days method): {years_trading:.6f}")

# CAGR calculation from backtest
cagr_calculated = (1 + total_return) ** (1 / years_trading) - 1

print(f"\nCalculated CAGR: {cagr_calculated:.6f} ({cagr_calculated*100:.2f}%)")

# Compare to reported
reported_cagr = metrics.iloc[0]['cagr']
print(f"Reported CAGR: {reported_cagr:.6f} ({reported_cagr*100:.2f}%)")

difference = abs(cagr_calculated - reported_cagr)
print(f"Difference: {difference:.6f}")

if difference < 0.00001:
    print("\n✓ CAGR VERIFIED - Matches using trading days method (252 days/year)")
else:
    print(f"\n✗ Still doesn't match")
    print(f"   Calculated: {cagr_calculated}")
    print(f"   Reported: {reported_cagr}")
