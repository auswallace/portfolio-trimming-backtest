#!/usr/bin/env python
"""
Sensitivity Analysis: Trim Threshold vs Trim Size

Generate heatmaps showing how CAGR varies with:
- Trim threshold (50%, 75%, 100%, 125%, 150%, 200%)
- Trim size (10%, 15%, 20%, 25%, 30%)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*80)
print("SENSITIVITY ANALYSIS: TRIM THRESHOLD vs TRIM SIZE")
print("="*80)

# Configuration
START_DATE = '2015-01-01'
END_DATE = '2024-11-05'
INITIAL_CASH = 100000

# Parameter grid
TRIM_THRESHOLDS = [0.50, 0.75, 1.00, 1.25, 1.50, 2.00]
TRIM_SIZES = [0.10, 0.15, 0.20, 0.25, 0.30]
REINVEST_MODES = ['pro_rata', 'spy']  # Test just 2 modes for speed

# Portfolio config (realistic 60/40 index/stock allocation)
PORTFOLIO_CONFIG = {
    'SPY': 0.30,
    'QQQ': 0.20,
    'VOO': 0.10,
    'AAPL': 0.15,
    'MSFT': 0.15,
    'TSLA': 0.10
}

TICKERS = list(PORTFOLIO_CONFIG.keys())
DATA_DIR = 'data'

print(f"\n📊 Testing parameter grid:")
print(f"  Trim thresholds: {[f'{t*100:.0f}%' for t in TRIM_THRESHOLDS]}")
print(f"  Trim sizes: {[f'{s*100:.0f}%' for s in TRIM_SIZES]}")
print(f"  Reinvestment modes: {REINVEST_MODES}")
print(f"  Total combinations: {len(TRIM_THRESHOLDS)} × {len(TRIM_SIZES)} × {len(REINVEST_MODES)} = {len(TRIM_THRESHOLDS) * len(TRIM_SIZES) * len(REINVEST_MODES)}")

# Load data
print(f"\n📂 Loading data from {DATA_DIR}/...")
all_data = {}
for ticker in TICKERS:
    csv_file = f"{DATA_DIR}/{ticker}.csv"
    try:
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
        df.set_index('Date', inplace=True)
        start_dt = pd.to_datetime(START_DATE)
        end_dt = pd.to_datetime(END_DATE)
        ticker_data = df['Close'][(df.index >= start_dt) & (df.index <= end_dt)]
        all_data[ticker] = ticker_data
        print(f"  ✓ {ticker}: {len(ticker_data)} days")
    except Exception as e:
        print(f"  ✗ {ticker}: {str(e)[:50]}")

price_df = pd.DataFrame(all_data).ffill().dropna()
dates = price_df.index
valid_tickers = list(price_df.columns)

print(f"\n✓ Loaded {len(valid_tickers)} tickers, {len(dates)} trading days")

# Calculate initial positions
initial_shares = {}
for ticker in valid_tickers:
    allocation = INITIAL_CASH * PORTFOLIO_CONFIG.get(ticker, 1.0/len(valid_tickers))
    initial_shares[ticker] = allocation / price_df[ticker].iloc[0]

# Helper function
def run_threshold_strategy(threshold, trim_size, reinvest_mode):
    """Run a single threshold-based strategy"""
    holdings = {ticker: initial_shares[ticker] for ticker in valid_tickers}
    cost_basis = {ticker: price_df[ticker].iloc[0] for ticker in valid_tickers}
    cash = 0.0
    num_trims = 0

    for i, date in enumerate(dates):
        # Trim logic
        for ticker in valid_tickers:
            if holdings[ticker] <= 0:
                continue

            current_price = price_df[ticker].iloc[i]
            gain = (current_price - cost_basis[ticker]) / cost_basis[ticker]

            if gain >= threshold:
                shares_to_sell = holdings[ticker] * trim_size
                proceeds = shares_to_sell * current_price
                holdings[ticker] -= shares_to_sell
                num_trims += 1

                # Reinvest
                if reinvest_mode == 'cash':
                    cash += proceeds
                elif reinvest_mode == 'spy' and 'SPY' in valid_tickers:
                    holdings['SPY'] += proceeds / price_df['SPY'].iloc[i]
                elif reinvest_mode == 'pro_rata':
                    total_value = sum(holdings[t] * price_df[t].iloc[i] for t in valid_tickers)
                    for t in valid_tickers:
                        weight = (holdings[t] * price_df[t].iloc[i]) / total_value if total_value > 0 else 1.0/len(valid_tickers)
                        holdings[t] += (proceeds * weight) / price_df[t].iloc[i]

                cost_basis[ticker] = current_price * 1.05

    # Calculate final value
    final_value = sum(holdings[t] * price_df[t].iloc[-1] for t in valid_tickers) + cash

    # Calculate CAGR
    years = len(dates) / 252
    cagr = (final_value / INITIAL_CASH) ** (1 / years) - 1

    return {'final_value': final_value, 'cagr': cagr, 'num_trims': num_trims}

# Run sensitivity analysis
print("\n🔄 Running sensitivity analysis...")
results = {}

total_runs = len(TRIM_THRESHOLDS) * len(TRIM_SIZES) * len(REINVEST_MODES)
run_count = 0

for mode in REINVEST_MODES:
    mode_results = np.zeros((len(TRIM_SIZES), len(TRIM_THRESHOLDS)))

    for i, trim_size in enumerate(TRIM_SIZES):
        for j, threshold in enumerate(TRIM_THRESHOLDS):
            run_count += 1
            metrics = run_threshold_strategy(threshold, trim_size, mode)
            mode_results[i, j] = metrics['cagr']

            if run_count % 6 == 0 or run_count == total_runs:
                print(f"  Progress: {run_count}/{total_runs} ({run_count/total_runs*100:.0f}%)")

    results[mode] = mode_results

print("\n✓ Sensitivity analysis complete!")

# Generate heatmaps
print("\n📊 Generating heatmaps...")

os.makedirs('visualizations', exist_ok=True)

# Set style
sns.set_style('whitegrid')
sns.set_palette('RdYlGn')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

for mode, data in results.items():
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create heatmap
    sns.heatmap(
        data * 100,  # Convert to percentage
        xticklabels=[f'{t*100:.0f}%' for t in TRIM_THRESHOLDS],
        yticklabels=[f'{s*100:.0f}%' for s in TRIM_SIZES],
        annot=True,
        fmt='.1f',
        cmap='RdYlGn',
        center=21.69,  # Center on buy-and-hold CAGR
        cbar_kws={'label': 'CAGR (%)'},
        ax=ax
    )

    ax.set_title(f'Sensitivity Analysis: Trim Threshold vs Trim Size\nReinvestment: {mode.upper()}',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Trim Threshold (Gain %)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Trim Size (% of Position)', fontsize=12, fontweight='bold')

    # Add reference line for buy-and-hold CAGR
    ax.text(0.5, -0.15, 'Buy-and-Hold CAGR: 21.69%',
            transform=ax.transAxes, ha='center', fontsize=10, style='italic')

    plt.tight_layout()
    filename = f'visualizations/sensitivity_heatmap_{mode}.png'
    plt.savefig(filename, bbox_inches='tight')
    print(f"  ✓ Saved: {filename}")
    plt.close()

# Find optimal parameters
print("\n🏆 Optimal Parameter Combinations:\n")
for mode, data in results.items():
    max_idx = np.unravel_index(np.argmax(data), data.shape)
    optimal_size = TRIM_SIZES[max_idx[0]]
    optimal_threshold = TRIM_THRESHOLDS[max_idx[1]]
    optimal_cagr = data[max_idx]

    print(f"{mode.upper()}:")
    print(f"  Optimal threshold: {optimal_threshold*100:.0f}%")
    print(f"  Optimal trim size: {optimal_size*100:.0f}%")
    print(f"  CAGR: {optimal_cagr*100:.2f}%")
    print(f"  vs Buy-and-Hold: {(optimal_cagr - 0.2169)*100:+.2f}%")
    print()

print("="*80)
print("✅ SENSITIVITY ANALYSIS COMPLETE")
print("="*80)
