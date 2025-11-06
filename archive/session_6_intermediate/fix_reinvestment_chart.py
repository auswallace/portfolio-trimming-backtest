#!/usr/bin/env python3
"""
Fix and regenerate the reinvestment mode comparison chart.

Fixes:
1. Spelling: "Volatitlity-2.5x stategy: Reienbvestment" → "Volatility-2.5x Strategy: Reinvestment Mode Comparison"
2. NaN values on x-axis (filter them out)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style('whitegrid')
sns.set_palette('colorblind')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# Read results (first column is the index with strategy names)
df = pd.read_csv('results_index_focus/index_focus_results.csv', index_col=0)
df['Strategy'] = df.index

# Filter for Volatility-2.5x strategies only
vol_25x = df[df['Strategy'].str.contains('Volatility-2.5x', case=False, na=False)].copy()

# Extract reinvestment mode from strategy name
def extract_reinvest_mode(strategy):
    """Extract reinvestment mode from strategy string"""
    if pd.isna(strategy):
        return None
    if 'pro-rata' in strategy.lower():
        return 'Pro-Rata'
    elif 'drip' in strategy.lower():
        return 'DRIP'
    elif 'spy' in strategy.lower():
        return 'SPY'
    elif 'dip-buy' in strategy.lower():
        return 'Dip-Buy-5%'
    elif 'yield-volatility' in strategy.lower():
        return 'Yield-Volatility'
    elif 'cash' in strategy.lower():
        return 'Cash'
    else:
        return 'Other'

vol_25x['Reinvestment_Mode'] = vol_25x['Strategy'].apply(extract_reinvest_mode)

# Remove any NaN values
vol_25x = vol_25x[vol_25x['Reinvestment_Mode'].notna()]
vol_25x = vol_25x[vol_25x['cagr'].notna()]

# Sort by CAGR descending
vol_25x = vol_25x.sort_values('cagr', ascending=False)

print(f"Found {len(vol_25x)} Volatility-2.5x strategies:")
print(vol_25x[['Strategy', 'Reinvestment_Mode', 'cagr', 'sharpe_ratio', 'max_drawdown']])

# Create bar chart
fig, ax = plt.subplots(figsize=(12, 6))

x_pos = np.arange(len(vol_25x))
bars = ax.bar(x_pos, vol_25x['cagr'] * 100, color=sns.color_palette('colorblind', len(vol_25x)))

# Customize
ax.set_xlabel('Reinvestment Mode', fontsize=12, fontweight='bold')
ax.set_ylabel('CAGR (%)', fontsize=12, fontweight='bold')
ax.set_title('Volatility-2.5x Strategy: Reinvestment Mode Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x_pos)
ax.set_xticklabels(vol_25x['Reinvestment_Mode'], rotation=45, ha='right')
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (idx, row) in enumerate(vol_25x.iterrows()):
    height = row['cagr'] * 100
    ax.text(i, height + 0.3, f'{height:.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Add horizontal line for buy-and-hold baseline
bh_cagr = df[df['Strategy'].str.contains('Buy-and-Hold', case=False, na=False)]['cagr'].values[0] * 100
ax.axhline(y=bh_cagr, color='red', linestyle='--', linewidth=2, label=f'Buy-and-Hold ({bh_cagr:.1f}%)')
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig('visualizations/reinvestment_mode_comparison.png', bbox_inches='tight', dpi=300)
print(f"\n✅ Fixed chart saved: visualizations/reinvestment_mode_comparison.png")
print(f"📊 Chart shows {len(vol_25x)} reinvestment modes (no NaN values)")
print(f"🔤 Title corrected: 'Volatility-2.5x Strategy: Reinvestment Mode Comparison'")

plt.close()
