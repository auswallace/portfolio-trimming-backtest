#!/usr/bin/env python
"""
Portfolio Trimming Strategy - Professional Visualization Generator

Generates publication-quality charts for technical research report.
All charts saved to visualizations/ directory at 300 DPI.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Set professional styling
sns.set_style('whitegrid')
sns.set_palette('colorblind')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

# Directories
RESULTS_DIR_PHASE1 = 'results_real_data'
RESULTS_DIR_PHASE3 = 'results_index_focus'
MANUAL_DATA_DIR = 'manual_data'
VIZ_DIR = 'visualizations'

os.makedirs(VIZ_DIR, exist_ok=True)

print("="*80)
print("PORTFOLIO TRIMMING STRATEGY - VISUALIZATION GENERATOR")
print("="*80)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n📂 Loading results data...")

# Phase 1 results (NVDA-dominated portfolio)
phase1_results = pd.read_csv(f'{RESULTS_DIR_PHASE1}/real_data_results.csv', index_col=0)
print(f"  ✓ Phase 1 results: {len(phase1_results)} strategies")

# Phase 3 results (index-focused portfolio)
phase3_results = pd.read_csv(f'{RESULTS_DIR_PHASE3}/index_focus_results.csv', index_col=0)
print(f"  ✓ Phase 3 results: {len(phase3_results)} strategies")

# Load historical price data for NVDA and SPY
nvda_df = pd.read_csv(f'{MANUAL_DATA_DIR}/NVDA.csv')
nvda_df['Date'] = pd.to_datetime(nvda_df['Date'], utc=True).dt.tz_localize(None)
nvda_df.set_index('Date', inplace=True)

spy_df = pd.read_csv(f'{MANUAL_DATA_DIR}/SPY.csv')
spy_df['Date'] = pd.to_datetime(spy_df['Date'], utc=True).dt.tz_localize(None)
spy_df.set_index('Date', inplace=True)

print(f"  ✓ NVDA price data: {len(nvda_df)} days")
print(f"  ✓ SPY price data: {len(spy_df)} days")

# ============================================================================
# CHART 1: Performance Bars - Phase 1
# ============================================================================

print("\n📊 Generating Chart 1: Phase 1 Performance Comparison...")

fig, ax = plt.subplots(figsize=(14, 8))

# Prepare data
phase1_sorted = phase1_results.sort_values('final_value', ascending=True)
strategies = phase1_sorted.index
values = phase1_sorted['final_value'] / 1e6  # Convert to millions

# Color coding: gold for buy-and-hold, blues for others
colors = ['#FFD700' if 'Buy-and-Hold' in s else '#4C72B0' for s in strategies]

# Create horizontal bar chart
bars = ax.barh(strategies, values, color=colors, edgecolor='black', linewidth=0.5)

# Add value labels
for i, (strategy, value) in enumerate(zip(strategies, values)):
    ax.text(value + 0.1, i, f'${value:.2f}M', va='center', fontsize=9)

ax.set_xlabel('Final Portfolio Value ($ Millions)', fontsize=12, fontweight='bold')
ax.set_title('Phase 1: Performance Comparison - NVDA-Dominated Portfolio\nAll 13 Strategies (2015-2024, $100K Initial Capital)',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='x')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#FFD700', edgecolor='black', label='Buy-and-Hold (Baseline)'),
    Patch(facecolor='#4C72B0', edgecolor='black', label='Trimming Strategies')
]
ax.legend(handles=legend_elements, loc='lower right')

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/phase1_performance_comparison.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/phase1_performance_comparison.png")

# ============================================================================
# CHART 2: Performance Bars - Phase 3
# ============================================================================

print("\n📊 Generating Chart 2: Phase 3 Performance Comparison...")

fig, ax = plt.subplots(figsize=(14, 8))

# Prepare data
phase3_sorted = phase3_results.sort_values('final_value', ascending=True)
strategies = phase3_sorted.index
values = phase3_sorted['final_value'] / 1e3  # Convert to thousands

# Color coding: gold for buy-and-hold, greens for others
colors = ['#FFD700' if 'Buy-and-Hold' in s else '#55A868' for s in strategies]

# Create horizontal bar chart
bars = ax.barh(strategies, values, color=colors, edgecolor='black', linewidth=0.5)

# Add value labels
for i, (strategy, value) in enumerate(zip(strategies, values)):
    ax.text(value + 5, i, f'${value:.0f}K', va='center', fontsize=9)

ax.set_xlabel('Final Portfolio Value ($ Thousands)', fontsize=12, fontweight='bold')
ax.set_title('Phase 3: Performance Comparison - Realistic Index-Focused Portfolio\nAll 13 Strategies (2015-2024, $100K Initial Capital)',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='x')

# Add legend
legend_elements = [
    Patch(facecolor='#FFD700', edgecolor='black', label='Buy-and-Hold (Baseline)'),
    Patch(facecolor='#55A868', edgecolor='black', label='Trimming Strategies')
]
ax.legend(handles=legend_elements, loc='lower right')

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/phase3_performance_comparison.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/phase3_performance_comparison.png")

# ============================================================================
# CHART 3: NVDA Price Journey with Hypothetical Trim Points
# ============================================================================

print("\n📊 Generating Chart 3: NVDA Price Journey...")

fig, ax = plt.subplots(figsize=(14, 8))

# Plot NVDA price
nvda_price = nvda_df['Close']
ax.plot(nvda_price.index, nvda_price, color='#2E8B57', linewidth=2, label='NVDA Price')

# Calculate and mark hypothetical trim points at +50%, +100%, +150%
start_price = nvda_price.iloc[0]
thresholds = [0.50, 1.00, 1.50]
threshold_colors = ['#FFA500', '#FF6347', '#DC143C']
threshold_labels = ['+50%', '+100%', '+150%']

# Track when each threshold would be triggered
for threshold, color, label in zip(thresholds, threshold_colors, threshold_labels):
    target_price = start_price * (1 + threshold)
    # Find first date when price crosses threshold
    crossing_points = nvda_price[nvda_price >= target_price]

    if len(crossing_points) > 0:
        first_cross_date = crossing_points.index[0]
        first_cross_price = crossing_points.iloc[0]

        # Mark the point
        ax.scatter(first_cross_date, first_cross_price, s=200, color=color,
                  marker='*', zorder=5, edgecolors='black', linewidths=1.5,
                  label=f'{label} Trim Trigger (${target_price:.2f})')

        # Add horizontal line for threshold
        ax.axhline(y=target_price, color=color, linestyle='--', alpha=0.3, linewidth=1)

# Mark start and end prices
ax.scatter(nvda_price.index[0], start_price, s=150, color='green',
          marker='o', zorder=5, edgecolors='black', linewidths=1.5,
          label=f'Start: ${start_price:.2f}')
ax.scatter(nvda_price.index[-1], nvda_price.iloc[-1], s=150, color='red',
          marker='o', zorder=5, edgecolors='black', linewidths=1.5,
          label=f'End: ${nvda_price.iloc[-1]:.2f}')

# Calculate total return
total_return = ((nvda_price.iloc[-1] / start_price) - 1) * 100

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
ax.set_title(f'NVDA Price Journey: The Cost of Trimming a 280x Winner\n2015-2024 ({total_return:+,.0f}% Total Return)',
             fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_yscale('log')  # Log scale to show full range

# Format y-axis
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/nvda_price_journey.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/nvda_price_journey.png")

# ============================================================================
# CHART 4: Risk-Return Scatter Plot
# ============================================================================

print("\n📊 Generating Chart 4: Risk-Return Scatter Plot...")

fig, ax = plt.subplots(figsize=(12, 8))

# Combine data from both phases
phase1_plot = phase1_results.copy()
phase1_plot['phase'] = 'Phase 1: NVDA-Dominated'

phase3_plot = phase3_results.copy()
phase3_plot['phase'] = 'Phase 3: Index-Focused'

combined = pd.concat([phase1_plot, phase3_plot])

# Scatter plot
for phase, color, marker in [('Phase 1: NVDA-Dominated', '#4C72B0', 'o'),
                               ('Phase 3: Index-Focused', '#55A868', 's')]:
    data = combined[combined['phase'] == phase]
    ax.scatter(data['volatility'] * 100, data['cagr'] * 100,
              s=100, alpha=0.7, color=color, marker=marker,
              edgecolors='black', linewidths=0.5, label=phase)

# Highlight buy-and-hold strategies
bnh_phase1 = phase1_results.loc['Buy-and-Hold']
bnh_phase3 = phase3_results.loc['Buy-and-Hold']

ax.scatter(bnh_phase1['volatility'] * 100, bnh_phase1['cagr'] * 100,
          s=300, marker='*', color='gold', edgecolors='black', linewidths=2,
          label='Buy-and-Hold (Phase 1)', zorder=5)
ax.scatter(bnh_phase3['volatility'] * 100, bnh_phase3['cagr'] * 100,
          s=300, marker='*', color='orange', edgecolors='black', linewidths=2,
          label='Buy-and-Hold (Phase 3)', zorder=5)

ax.set_xlabel('Volatility (Annual Standard Deviation %)', fontsize=12, fontweight='bold')
ax.set_ylabel('CAGR (%)', fontsize=12, fontweight='bold')
ax.set_title('Risk-Return Trade-off: All Strategies Across Both Portfolio Types\nHigher is better (more return), Left is better (less risk)',
             fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='best', fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/risk_return_scatter.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/risk_return_scatter.png")

# ============================================================================
# CHART 5: Drawdown Comparison (Simulated from data)
# ============================================================================

print("\n📊 Generating Chart 5: Maximum Drawdown Comparison...")

fig, ax = plt.subplots(figsize=(12, 8))

# Create grouped bar chart for max drawdown
strategies_to_compare = [
    'Buy-and-Hold',
    'Trim@+50% (pro-rata)',
    'Trim@+100% (pro-rata)',
    'Trim@+150% (pro-rata)',
]

x = np.arange(len(strategies_to_compare))
width = 0.35

phase1_dd = [phase1_results.loc[s, 'max_drawdown'] * 100 for s in strategies_to_compare]
phase3_dd = [phase3_results.loc[s, 'max_drawdown'] * 100 for s in strategies_to_compare]

bars1 = ax.bar(x - width/2, phase1_dd, width, label='Phase 1: NVDA-Dominated',
               color='#4C72B0', edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + width/2, phase3_dd, width, label='Phase 3: Index-Focused',
               color='#55A868', edgecolor='black', linewidth=0.5)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height - 2,
               f'{height:.1f}%', ha='center', va='top', fontsize=9, color='white', fontweight='bold')

ax.set_ylabel('Maximum Drawdown (%)', fontsize=12, fontweight='bold')
ax.set_title('Maximum Drawdown Comparison: Risk Profiles Across Strategies\nLower (less negative) is better',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(strategies_to_compare, rotation=45, ha='right')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3, axis='y')
ax.axhline(y=0, color='black', linewidth=0.8)

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/drawdown_comparison.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/drawdown_comparison.png")

# ============================================================================
# CHART 6: Sharpe Ratio Comparison
# ============================================================================

print("\n📊 Generating Chart 6: Sharpe Ratio Comparison...")

fig, ax = plt.subplots(figsize=(12, 8))

# Top 8 strategies by Sharpe in Phase 3
phase3_top_sharpe = phase3_results.nlargest(8, 'sharpe_ratio')

strategies = phase3_top_sharpe.index
sharpe_values = phase3_top_sharpe['sharpe_ratio']

# Color: gold for buy-and-hold, green for others
colors = ['#FFD700' if 'Buy-and-Hold' in s else '#55A868' for s in strategies]

bars = ax.barh(strategies, sharpe_values, color=colors, edgecolor='black', linewidth=0.5)

# Add value labels
for i, (strategy, value) in enumerate(zip(strategies, sharpe_values)):
    ax.text(value + 0.02, i, f'{value:.3f}', va='center', fontsize=9)

ax.set_xlabel('Sharpe Ratio', fontsize=12, fontweight='bold')
ax.set_title('Risk-Adjusted Returns: Phase 3 Strategies by Sharpe Ratio\nHigher is better (more return per unit of risk)',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='x')

# Add reference line at Sharpe = 1.0
ax.axvline(x=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.5, label='Sharpe = 1.0 (excellent)')
ax.legend(loc='lower right')

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/sharpe_ratio_comparison.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/sharpe_ratio_comparison.png")

# ============================================================================
# CHART 7: Dip-Buy Timeline (SPY with 5% drop markers)
# ============================================================================

print("\n📊 Generating Chart 7: Dip-Buy Timeline...")

fig, ax = plt.subplots(figsize=(14, 8))

# Plot SPY price
spy_price = spy_df['Close']
ax.plot(spy_price.index, spy_price, color='#1f77b4', linewidth=2, label='S&P 500 (SPY)', alpha=0.7)

# Simulate 5% drop detection
spy_recent_high = spy_price.iloc[0]
dip_buy_events = []

for i, date in enumerate(spy_price.index):
    current_price = spy_price.iloc[i]

    # Track new highs
    if current_price > spy_recent_high:
        spy_recent_high = current_price

    # Check for 5% drop
    drop_pct = (spy_recent_high - current_price) / spy_recent_high

    if drop_pct >= 0.05 and (len(dip_buy_events) == 0 or
                             (date - dip_buy_events[-1]['date']).days > 30):
        dip_buy_events.append({
            'date': date,
            'price': current_price,
            'drop_pct': drop_pct,
            'from_high': spy_recent_high
        })
        # Reset high after buy
        spy_recent_high = current_price

# Mark dip-buy events
for event in dip_buy_events:
    ax.scatter(event['date'], event['price'], s=200, color='red',
              marker='v', zorder=5, edgecolors='black', linewidths=1.5)
    ax.annotate(f"{event['drop_pct']*100:.1f}%",
               xy=(event['date'], event['price']),
               xytext=(0, -20), textcoords='offset points',
               ha='center', fontsize=8, color='red', fontweight='bold')

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('SPY Price ($)', fontsize=12, fontweight='bold')
ax.set_title(f'Dip-Buy Strategy: 5% S&P 500 Drop Triggers (2015-2024)\n{len(dip_buy_events)} buy signals detected',
             fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)

# Add text box with stats
avg_drop = np.mean([e['drop_pct'] for e in dip_buy_events]) * 100
textstr = f'Total Dip-Buys: {len(dip_buy_events)}\nAvg Drop: {avg_drop:.2f}%'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/dip_buy_timeline.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/dip_buy_timeline.png")

# ============================================================================
# CHART 8: Trim Frequency Analysis
# ============================================================================

print("\n📊 Generating Chart 8: Trim Frequency by Strategy...")

fig, ax = plt.subplots(figsize=(12, 8))

# Get trim counts for different strategies (from Phase 1)
trim_strategies = [
    ('Trim@+50% (pro-rata)', phase1_results.loc['Trim@+50% (pro-rata)', 'num_trades']),
    ('Trim@+100% (pro-rata)', phase1_results.loc['Trim@+100% (pro-rata)', 'num_trades']),
    ('Trim@+150% (pro-rata)', phase1_results.loc['Trim@+150% (pro-rata)', 'num_trades']),
]

strategies = [s[0] for s in trim_strategies]
counts_phase1 = [s[1] for s in trim_strategies]

# Get Phase 3 counts
counts_phase3 = [
    phase3_results.loc['Trim@+50% (pro-rata)', 'num_trades'],
    phase3_results.loc['Trim@+100% (pro-rata)', 'num_trades'],
    phase3_results.loc['Trim@+150% (pro-rata)', 'num_trades'],
]

x = np.arange(len(strategies))
width = 0.35

bars1 = ax.bar(x - width/2, counts_phase1, width, label='Phase 1: NVDA-Dominated',
               color='#4C72B0', edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + width/2, counts_phase3, width, label='Phase 3: Index-Focused',
               color='#55A868', edgecolor='black', linewidth=0.5)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
               f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_ylabel('Number of Trim Events (10 years)', fontsize=12, fontweight='bold')
ax.set_title('Trim Frequency by Threshold: How Often Did Trimming Occur?\nLower thresholds trigger more frequent trims',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(strategies, rotation=0)
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/trim_frequency_analysis.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/trim_frequency_analysis.png")

# ============================================================================
# CHART 9: CAGR Comparison - Phase 1 vs Phase 3
# ============================================================================

print("\n📊 Generating Chart 9: CAGR Comparison...")

fig, ax = plt.subplots(figsize=(14, 8))

# Select key strategies for comparison
key_strategies = [
    'Buy-and-Hold',
    'Trim@+50% (pro-rata)',
    'Trim@+100% (pro-rata)',
    'Trim@+150% (pro-rata)',
    'Trim@+150% (dip-buy-5pct)',
]

x = np.arange(len(key_strategies))
width = 0.35

cagr_phase1 = [phase1_results.loc[s, 'cagr'] * 100 for s in key_strategies]
cagr_phase3 = [phase3_results.loc[s, 'cagr'] * 100 for s in key_strategies]

bars1 = ax.bar(x - width/2, cagr_phase1, width, label='Phase 1: NVDA-Dominated',
               color='#4C72B0', edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + width/2, cagr_phase3, width, label='Phase 3: Index-Focused',
               color='#55A868', edgecolor='black', linewidth=0.5)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
               f'{height:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('CAGR (%)', fontsize=12, fontweight='bold')
ax.set_title('Compound Annual Growth Rate: Portfolio Composition Matters\nPhase 1 (NVDA-heavy) vs Phase 3 (Index-focused)',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(key_strategies, rotation=45, ha='right')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/cagr_comparison.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/cagr_comparison.png")

# ============================================================================
# CHART 10: The NVDA Effect - Contribution Analysis
# ============================================================================

print("\n📊 Generating Chart 10: NVDA Contribution Analysis...")

fig, ax = plt.subplots(figsize=(12, 8))

# Load all tickers for Phase 1 portfolio
tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']
ticker_returns = {}

for ticker in tickers:
    df = pd.read_csv(f'{MANUAL_DATA_DIR}/{ticker}.csv')
    df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    total_return = ((end_price / start_price) - 1) * 100
    ticker_returns[ticker] = total_return

# Create bar chart
tickers_sorted = sorted(ticker_returns.items(), key=lambda x: x[1], reverse=True)
tickers_names = [t[0] for t in tickers_sorted]
returns = [t[1] for t in tickers_sorted]

# Color NVDA differently
colors = ['#DC143C' if t == 'NVDA' else '#4C72B0' for t in tickers_names]

bars = ax.bar(tickers_names, returns, color=colors, edgecolor='black', linewidth=1)

# Add value labels
for bar, ret in zip(bars, returns):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 500,
           f'{ret:,.0f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Total Return 2015-2024 (%)', fontsize=12, fontweight='bold')
ax.set_title('The NVDA Effect: Why Trimming Failed in Phase 1\nNVDA gained 28,057% - trimming cut this winner far too early',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, max(returns) * 1.1)

# Add annotation for NVDA
ax.annotate('Monster Outlier:\n280x return',
           xy=(0, ticker_returns['NVDA']),
           xytext=(1.5, ticker_returns['NVDA'] * 0.7),
           fontsize=11, color='red', fontweight='bold',
           arrowprops=dict(arrowstyle='->', color='red', lw=2))

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/nvda_contribution_analysis.png', bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {VIZ_DIR}/nvda_contribution_analysis.png")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("✅ VISUALIZATION GENERATION COMPLETE")
print("="*80)
print(f"\n📊 Generated 10 professional charts in {VIZ_DIR}/:")
print("  1. phase1_performance_comparison.png - All strategies Phase 1")
print("  2. phase3_performance_comparison.png - All strategies Phase 3")
print("  3. nvda_price_journey.png - NVDA with trim points")
print("  4. risk_return_scatter.png - Risk vs return all strategies")
print("  5. drawdown_comparison.png - Maximum drawdown analysis")
print("  6. sharpe_ratio_comparison.png - Risk-adjusted returns")
print("  7. dip_buy_timeline.png - SPY with 5% drop markers")
print("  8. trim_frequency_analysis.png - How often trims occurred")
print("  9. cagr_comparison.png - Phase 1 vs Phase 3 returns")
print(" 10. nvda_contribution_analysis.png - Ticker returns breakdown")
print(f"\nAll charts saved at 300 DPI, publication quality.")
print(f"Ready for inclusion in TECHNICAL_REPORT.md\n")
