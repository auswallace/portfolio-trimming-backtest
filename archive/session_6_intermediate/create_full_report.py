#!/usr/bin/env python3
"""
Create comprehensive Jupyter notebook with all visualizations embedded
at appropriate narrative points.
"""

import json
import base64
from pathlib import Path

def encode_image(path):
    """Encode image file as base64 string"""
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def create_md_cell(text):
    """Create markdown cell"""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.split('\n') if isinstance(text, str) else text
    }

def create_img_cell(img_path, caption):
    """Create code cell with embedded image output"""
    img_b64 = encode_image(img_path)
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [{
            "data": {
                "image/png": img_b64,
                "text/plain": [f"<Figure: {caption}>"]
            },
            "metadata": {},
            "output_type": "display_data"
        }],
        "source": [
            f"# {caption}\n",
            "from IPython.display import Image, display\n",
            f"display(Image(filename='{img_path}', width=900))"
        ]
    }

# Read the markdown report
with open('BACKTEST_REPORT_DC_VOICE.md', 'r') as f:
    md = f.read()

# Initialize notebook
nb = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.9.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Split into sections
sections = md.split('\n## ')
header = sections[0]

# Add title
nb["cells"].append(create_md_cell(header))

# Process each major section and insert charts at appropriate points
for section in sections[1:]:
    section_title = section.split('\n')[0]
    section_content = '\n'.join(section.split('\n')[1:])

    # Add section header and content
    nb["cells"].append(create_md_cell(f"## {section_title}\n\n{section_content}"))

    # Insert relevant charts based on section
    if "The Journey" in section_title:
        # Add performance waterfall showing all 42 strategies
        if Path('visualizations/performance_waterfall_top20.png').exists():
            nb["cells"].append(create_img_cell(
                'visualizations/performance_waterfall_top20.png',
                'Performance Waterfall - Top 20 Strategies (52% Spread from Best to Worst)'
            ))

    elif "The Breakthrough" in section_title:
        # Add risk-return scatter and cumulative returns
        if Path('visualizations/risk_return_scatter.png').exists():
            nb["cells"].append(create_img_cell(
                'visualizations/risk_return_scatter.png',
                'Risk-Return Efficient Frontier: Volatility vs CAGR'
            ))
        if Path('visualizations/impressive_cumulative_returns.png').exists():
            nb["cells"].append(create_img_cell(
                'visualizations/impressive_cumulative_returns.png',
                'Cumulative Returns Over Time (2015-2024)'
            ))

    elif "Reinvestment Modes" in section_title:
        # Add reinvestment mode comparison
        if Path('visualizations/reinvestment_mode_comparison.png').exists():
            nb["cells"].append(create_img_cell(
                'visualizations/reinvestment_mode_comparison.png',
                'Reinvestment Mode Impact: Why Pro-Rata Dominates'
            ))

    elif "Trade-Off Nobody Talks About" in section_title:
        # Add rolling returns showing volatility tradeoff
        if Path('visualizations/impressive_rolling_returns.png').exists():
            nb["cells"].append(create_img_cell(
                'visualizations/impressive_rolling_returns.png',
                'Rolling 1-Year Returns: Volatility Strategies Have Higher Beta'
            ))

    elif "Who Should Use Which Strategy" in section_title:
        # Add sensitivity heatmaps
        if Path('visualizations/sensitivity_heatmap_pro_rata.png').exists():
            nb["cells"].append(create_img_cell(
                'visualizations/sensitivity_heatmap_pro_rata.png',
                'Sensitivity Analysis: Volatility Multiplier Impact (Pro-Rata Reinvestment)'
            ))
        if Path('visualizations/sensitivity_heatmap_spy.png').exists():
            nb["cells"].append(create_img_cell(
                'visualizations/sensitivity_heatmap_spy.png',
                'Sensitivity Analysis: Volatility Multiplier Impact (SPY Reinvestment)'
            ))

    elif "The Limitations" in section_title:
        # Add drawdown timeline
        if Path('visualizations/impressive_drawdown_timeline.png').exists():
            nb["cells"].append(create_img_cell(
                'visualizations/impressive_drawdown_timeline.png',
                'Drawdown Timeline with Major Market Events'
            ))

# Save notebook
output_path = 'BACKTEST_REPORT_DC_VOICE.ipynb'
with open(output_path, 'w') as f:
    json.dump(nb, f, indent=2)

print(f"✅ Complete Jupyter notebook created: {output_path}")
print(f"📊 Total cells: {len(nb['cells'])}")
print(f"📝 Markdown cells: {sum(1 for c in nb['cells'] if c['cell_type'] == 'markdown')}")
print(f"🖼️  Image cells: {sum(1 for c in nb['cells'] if c['cell_type'] == 'code')}")
print(f"📈 Embedded charts:")
charts = [c for c in nb['cells'] if c['cell_type'] == 'code']
for i, chart in enumerate(charts, 1):
    caption = chart['source'][0].replace('# ', '')
    print(f"   {i}. {caption}")
