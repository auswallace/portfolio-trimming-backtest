#!/usr/bin/env python
"""
Add insightful interpretations after each chart in the notebook
"""

import json

with open('COMPREHENSIVE_BACKTEST_REPORT.ipynb', 'r') as f:
    notebook = json.load(f)

print("=" * 80)
print("ADDING CHART INSIGHTS TO COMPREHENSIVE_BACKTEST_REPORT.ipynb")
print("=" * 80)

insights_added = []

# Chart insights to add after specific visualizations
chart_insights = {
    'performance_waterfall_top20.png': {
        'title': '**Chart Insight: Strategy Performance Hierarchy**',
        'insights': [
            '- **Top 3 are all volatility-based**: The clustering at the top shows volatility strategies dominate',
            '- **Color pattern matters**: Red (volatility) outperforms green (momentum) which outperforms blue (threshold)',
            '- **Buy-and-hold sits in middle**: Beats 22 strategies, loses to 20 strategies - neither terrible nor optimal',
            '- **Wide spread**: $1.05M (best) vs $155K (worst) = 6.7× difference shows strategy choice is critical'
        ]
    },
    'reinvestment_mode_comparison.png': {
        'title': '**Chart Insight: Reinvestment Mode Impact**',
        'insights': [
            '- **Pro-rata and drip dominate**: Top 2 modes differ by only 0.7% CAGR (26.98% vs 26.24%)',
            '- **Cash is catastrophic**: 6.43% CAGR = 76% underperformance vs pro-rata',
            '- **The gap is massive**: Pro-rata (26.98%) → dip-buy (15.48%) = 11.5% CAGR penalty for waiting',
            '- **SPY reinvestment okay**: 20.21% CAGR still beats inflation, but gives up 6.8% vs pro-rata',
            '- **Lesson**: Reinvest immediately, preferably pro-rata or gradually (drip)'
        ]
    },
    'risk_return_scatter.png': {
        'title': '**Chart Insight: Risk-Return Tradeoffs**',
        'insights': [
            '- **Volatility strategies push frontier**: Red dots (volatility) achieve highest CAGR for given volatility',
            '- **Marker size = Sharpe ratio**: Larger markers are more efficient, notice baseline (orange) is relatively small',
            '- **Threshold strategies cluster tight**: Blue dots form tight cluster near buy-and-hold (similar risk/return)',
            '- **No "free lunch"**: Higher returns come with higher volatility - but Sharpe ratios stay reasonable (0.8-0.9)',
            '- **Efficient frontier**: Volatility-2.5× sits on upper-right frontier - you cannot do much better without leverage'
        ]
    },
    'trim_frequency_analysis.png': {
        'title': '**Chart Insight: The Goldilocks Zone**',
        'insights': [
            '- **Sweet spot exists**: 40-60 trims (green zone) captures the best performers',
            '- **Too few trims (<15)**: Misses opportunities, hovers around buy-and-hold performance',
            '- **Too many trims (>200)**: Excessive turnover erodes returns, drops below buy-and-hold',
            '- **Volatility-2.5× nails it**: 47 trims = center of optimal range',
            '- **Momentum struggles**: 109 trims puts it in "too many" territory (19.7% CAGR)',
            '- **Practical takeaway**: Aim for ~5 trims per year (50 over 10 years)'
        ]
    },
    'sensitivity_heatmap_pro_rata.png': {
        'title': '**Chart Insight: Optimal Parameters Revealed**',
        'insights': [
            '- **Top-right corner wins**: Higher thresholds (150-200%) + smaller trims (10%) = best CAGR',
            '- **20% trim size is suboptimal**: Every threshold performs better at 10-15% trim size',
            '- **The main backtest used 20%**: This means our results are CONSERVATIVE - could be 1-2% better',
            '- **Threshold matters less than trim size**: Horizontal bands stronger than vertical',
            '- **Actionable insight**: Use 10-15% trims, be patient with thresholds (100-150%)'
        ]
    }
}

# Add insights after chart cells
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        # Check if this cell generates a chart
        for chart_file, insight_data in chart_insights.items():
            if chart_file in source and 'plt.show()' in source:
                # Check if next cell is already an insight
                if i + 1 < len(notebook['cells']):
                    next_cell_source = ''.join(notebook['cells'][i + 1].get('source', []))
                    if '**Chart Insight' in next_cell_source:
                        print(f"  ⊘ Insight already exists after {chart_file}")
                        continue

                # Add insight cell after this chart
                insight_cell = {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': [insight_data['title'] + '\n\n']
                }
                for insight in insight_data['insights']:
                    insight_cell['source'].append(insight + '\n')

                notebook['cells'].insert(i + 1, insight_cell)
                insights_added.append(f"✓ Added insight after {chart_file}")
                print(f"  ✓ Added insight after {chart_file}")
                break

# Add insight after cumulative growth chart
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        if 'cumulative_growth_baseline.png' in source and 'plt.show()' in source:
            if i + 1 < len(notebook['cells']):
                next_cell_source = ''.join(notebook['cells'][i + 1].get('source', []))
                if '**Chart Insight' not in next_cell_source:
                    insight_cell = {
                        'cell_type': 'markdown',
                        'metadata': {},
                        'source': [
                            '**Chart Insight: Cumulative Growth Pattern**\n',
                            '\n',
                            '- **Steady upward climb**: Buy-and-hold shows consistent growth with volatility\n',
                            '- **No time series for trimming strategies**: We show final values as reference lines (red dashed/dotted)\n',
                            '- **The gap**: Volatility-2.5× final values are ~$350k above buy-and-hold line\n',
                            '- **COVID crash visible**: Sharp dip in March 2020, quick recovery\n',
                            '- **Acceleration in 2020-2021**: Steeper slope = higher growth rate during stimulus era'
                        ]
                    }
                    notebook['cells'].insert(i + 1, insight_cell)
                    insights_added.append("✓ Added insight after cumulative growth chart")
                    print("  ✓ Added insight after cumulative growth chart")
            break

# Add insight after strategy type summary table
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        if 'type_summary' in source and 'groupby' in source:
            if i + 1 < len(notebook['cells']):
                next_cell_source = ''.join(notebook['cells'][i + 1].get('source', []))
                if '**Table Insight' not in next_cell_source:
                    insight_cell = {
                        'cell_type': 'markdown',
                        'metadata': {},
                        'source': [
                            '**Table Insight: Strategy Type Performance Rankings**\n',
                            '\n',
                            '- **Volatility-Based**: Highest max ($1.05M), but also widest range (high variance across reinvestment modes)\n',
                            '- **Threshold-Based**: Most consistent, tight range around buy-and-hold\n',
                            '- **Momentum-Guided**: Solid but unspectacular, too many trims (109 avg)\n',
                            '- **Average trade count matters**: Volatility strategies trade 2-6× more than thresholds\n',
                            '- **Takeaway**: If you can monitor volatility, go volatility-based. Otherwise, stick with simple thresholds.'
                        ]
                    }
                    notebook['cells'].insert(i + 1, insight_cell)
                    insights_added.append("✓ Added insight after strategy type summary")
                    print("  ✓ Added insight after strategy type summary")
            break

# Save updated notebook
with open('COMPREHENSIVE_BACKTEST_REPORT.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)

print("\n" + "=" * 80)
print("INSIGHTS ADDED SUMMARY")
print("=" * 80)
for insight in insights_added:
    print(insight)

print(f"\n✅ Successfully added {len(insights_added)} chart insights")
print("=" * 80)
