#!/usr/bin/env python
"""
Diagnose metrics calculation bug in volatility-based strategies
"""

import pandas as pd
import numpy as np

# Read the results
results = pd.read_csv('results_index_focus/index_focus_results.csv', index_col=0)

print("="*80)
print("METRICS DIAGNOSIS")
print("="*80)

# Find problematic strategies
print("\n🔍 Strategies with suspicious metrics:\n")
suspicious = results[
    (results['sortino_ratio'] > 10) |
    (results['volatility'] > 10) |
    (results['sharpe_ratio'] < -0.5)
]

if len(suspicious) > 0:
    print(suspicious[['final_value', 'cagr', 'sharpe_ratio', 'sortino_ratio', 'volatility', 'num_trades', 'cash_held']])
else:
    print("No suspicious strategies found!")

# Check for NaN or inf values
print("\n\n🔍 Checking for NaN/Inf values:\n")
for col in results.columns:
    nan_count = results[col].isna().sum()
    inf_count = np.isinf(results[col]).sum()
    if nan_count > 0 or inf_count > 0:
        print(f"  {col}: {nan_count} NaN, {inf_count} Inf")

# Analyze volatility-based strategies specifically
print("\n\n🔍 Volatility-Based Strategy Analysis:\n")
vol_strategies = results[results.index.str.contains('Volatility-Based')]
print(vol_strategies[['final_value', 'cagr', 'sharpe_ratio', 'sortino_ratio', 'volatility', 'num_trades', 'cash_held']].to_string())

# Check cash held ratios
print("\n\n💰 Cash Held Analysis:\n")
results['cash_pct'] = (results['cash_held'] / results['final_value']) * 100
high_cash = results[results['cash_pct'] > 20].sort_values('cash_pct', ascending=False)
if len(high_cash) > 0:
    print("Strategies holding >20% cash:")
    print(high_cash[['final_value', 'cash_held', 'cash_pct']].to_string())
else:
    print("No strategies holding >20% cash")

print("\n" + "="*80)
