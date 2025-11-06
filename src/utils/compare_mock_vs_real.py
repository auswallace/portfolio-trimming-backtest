#!/usr/bin/env python
"""
Compare Mock Data Results vs Real Data Results
Shows side-by-side comparison to validate mock simulation quality
"""

import pandas as pd

print("="*80)
print("MOCK DATA vs REAL DATA COMPARISON")
print("="*80)

# Load results
try:
    mock_results = pd.read_csv('trimming_strategy_results_with_dip.csv', index_col=0)
    print("✓ Loaded mock data results")
except:
    print("✗ Could not load mock data results")
    print("  Expected file: trimming_strategy_results_with_dip.csv")
    mock_results = None

try:
    real_results = pd.read_csv('results_real_data/real_data_results.csv', index_col=0)
    print("✓ Loaded real data results")
except:
    print("✗ Could not load real data results")
    print("  Expected file: results_real_data/real_data_results.csv")
    real_results = None

if mock_results is None or real_results is None:
    print("\n❌ Need both mock and real data results to compare!")
    exit(1)

print("\n" + "="*80)
print("COMPARISON: YOUR 5% DIP-BUY STRATEGY")
print("="*80)

strategy_name = 'Trim@+50% (dip-buy-5pct)'

if strategy_name in mock_results.index and strategy_name in real_results.index:
    mock_row = mock_results.loc[strategy_name]
    real_row = real_results.loc[strategy_name]

    print(f"\n{'Metric':<20} {'Mock Data':<20} {'Real Data':<20} {'Difference':<15}")
    print("-"*80)

    metrics = ['final_value', 'cagr', 'sharpe_ratio', 'sortino_ratio', 'max_drawdown', 'volatility', 'num_trades']

    for metric in metrics:
        if metric in mock_row.index and metric in real_row.index:
            mock_val = mock_row[metric]
            real_val = real_row[metric]

            if metric == 'final_value':
                mock_str = f"${mock_val:,.0f}"
                real_str = f"${real_val:,.0f}"
                diff_str = f"${real_val - mock_val:+,.0f}"
            elif metric in ['cagr', 'sharpe_ratio', 'sortino_ratio', 'max_drawdown', 'volatility']:
                mock_str = f"{mock_val:.2%}" if abs(mock_val) < 1 else f"{mock_val:.2f}"
                real_str = f"{real_val:.2%}" if abs(real_val) < 1 else f"{real_val:.2f}"

                if abs(real_val) > 1:  # Ratios
                    diff_str = f"{real_val - mock_val:+.2f}"
                else:  # Percentages
                    diff_str = f"{(real_val - mock_val):.2%}"
            else:
                mock_str = f"{mock_val:.0f}"
                real_str = f"{real_val:.0f}"
                diff_str = f"{real_val - mock_val:+.0f}"

            print(f"{metric:<20} {mock_str:<20} {real_str:<20} {diff_str:<15}")

    print("\n" + "="*80)
    print("ALL STRATEGIES RANKING")
    print("="*80)

    print("\n📊 MOCK DATA - Top 5:")
    mock_top5 = mock_results.sort_values('final_value', ascending=False).head(5)
    print(mock_top5[['final_value', 'cagr']].to_string())

    print("\n📊 REAL DATA - Top 5:")
    real_top5 = real_results.sort_values('final_value', ascending=False).head(5)
    print(real_top5[['final_value', 'cagr']].to_string())

    print("\n" + "="*80)
    print("INSIGHTS")
    print("="*80)

    mock_winner = mock_results['final_value'].idxmax()
    real_winner = real_results['final_value'].idxmax()

    print(f"\n🥇 Winner (Mock Data): {mock_winner}")
    print(f"   Final Value: ${mock_results.loc[mock_winner, 'final_value']:,.0f}")

    print(f"\n🥇 Winner (Real Data): {real_winner}")
    print(f"   Final Value: ${real_results.loc[real_winner, 'final_value']:,.0f}")

    if mock_winner == real_winner:
        print(f"\n✅ SAME WINNER! The mock data accurately predicted the best strategy.")
    else:
        print(f"\n⚠️  Different winners. Mock data was close but real market dynamics differ.")

    # Check if dip-buy still wins
    if 'dip-buy' in real_winner.lower():
        print(f"\n🎉 DIP-BUY STRATEGY STILL WINS WITH REAL DATA!")
    else:
        print(f"\n📌 A different strategy won with real data.")

else:
    print(f"\n⚠️  Strategy '{strategy_name}' not found in results")
    print("\nAvailable strategies:")
    print("Mock:", list(mock_results.index))
    print("Real:", list(real_results.index))

print("\n✨ Comparison complete!")
