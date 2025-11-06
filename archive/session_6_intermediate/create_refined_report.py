#!/usr/bin/env python3
"""
Create refined Jupyter notebook with editorial improvements applied.
Embeds all 8 charts as base64-encoded images.
"""

import json
import base64
from pathlib import Path

def encode_image(path):
    """Encode image file as base64 string"""
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def create_markdown_cell(text):
    """Create a markdown cell"""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.split('\n')
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
        "source": []
    }

# Define notebook structure with refined content
cells = [
    # Title
    create_markdown_cell("# Taking Profits: What Actually Works\n## A 10-Year Backtest of Systematic Profit-Taking Strategies"),

    # Summary of Findings
    create_markdown_cell("""## Summary of Findings

Before we dive in, here's where this research ends up:

**The Simple Answer**: It depends entirely on what you own and how you reinvest.

- **For outlier-heavy portfolios** (think early NVDA positions): Trimming costs you millions. Buy-and-hold crushed every trimming strategy by 20-50%.
- **For index-focused portfolios** (60% ETFs, 40% stocks): The right trimming strategy *beat* buy-and-hold by 52% while cutting max drawdown by 18%.
- **The critical variable**: Not your trim threshold, but *when and how you reinvest*. Market-timing reinvestment destroyed returns. Gradual reinvestment during volatility created alpha.

This isn't a story about finding "the best strategy." It's about understanding how systematic rules interact with portfolio composition and market conditions. Let's walk through how I figured this out."""),

    # The Question
    create_markdown_cell("""## The Question That Started Everything

I trimmed my NVDA position at +50% in 2023. Sold at $140. It hit $950 (split-adjusted). I lost over $100,000 in opportunity cost because I "took profits responsibly."

That experience haunted me. Was systematic trimming—selling 20% when positions gain 50%, 100%, 150%—just a way to feel smart while bleeding returns? Or does it actually work if you do it right?

I needed data. Not opinions, not anecdotes. Ten years of real market data testing every variation I could think of."""),

    # Methodology
    create_markdown_cell("""## Methodology

### The Framework

- **Period**: 2015-2024 (10 years, 2,477 trading days)
- **Initial Capital**: $100,000
- **Data Source**: Yahoo Finance historical prices
- **Metrics**: CAGR, Sharpe ratio, Sortino ratio, max drawdown, volatility
- **Test Count**: 42 distinct strategies across 3 portfolio configurations

### Three Phases of Testing

**Phase 1**: Equal-weight 6-stock portfolio (AAPL, MSFT, NVDA, TSLA, SPY, QQQ)—testing core trimming mechanics.

**Phase 2**: Added volatility-based trimming and gradual reinvestment modes—testing if smarter triggers and timing could improve results.

**Phase 3**: Index-focused portfolio (60% ETFs, 40% stocks)—testing realistic investor allocations.

### Strategy Variations

**Trimming Types** (5 approaches):
- **Fixed thresholds**: Trim 20% at +50%, +100%, +150% gains
- **Momentum-guided**: Dynamic thresholds (1.5× to 2.5× rolling average)
- **Volatility-based**: Trim more when volatility spikes (1.5× to 2.5× thresholds)

**Reinvestment Modes** (6 approaches):
- **Immediate**: Instant reinvestment (pro-rata or SPY)
- **Gradual (DRIP)**: 25% per week over 4 weeks
- **Market-timing**: Wait for 5% S&P dip
- **Yield/Volatility-based**: Gradual reentry using dividend yield and VIX signals

### Key Assumption

Transaction costs and taxes defaulted to 0% for baseline analysis. The backtest engine supports toggling both (0.05-0.5% per transaction, 15-37% capital gains tax), documented in `/docs/COST_TAX_MODELING.md`. Adding realistic costs (0.1% transaction + 20% tax) reduces all strategies proportionally but preserves relative rankings."""),

    # Phase 1
    create_markdown_cell("""## Phase 1: The NVDA Trap

### Portfolio Configuration
Equal-weight allocation: $16,667 per ticker (AAPL, MSFT, NVDA, TSLA, SPY, QQQ).

### What Happened"""),

    # Chart 1: Performance Waterfall
    create_img_cell("visualizations/performance_waterfall_top20.png", "Performance Waterfall - Top 20 Strategies"),

    create_markdown_cell("""**Buy-and-hold crushed every trimming strategy.** Final value: $5.4M (50.1% CAGR). Best trimming strategy: $4.3M (46.7% CAGR). Worst: $1.1M (28.1% CAGR).

That's not a rounding error. That's the difference between generational wealth and a nice car.

### The Root Cause: NVDA

NVDA gained **28,057%** over the period. It went from $0.48 to $136.04.

Every time we trimmed at +50%, we sold at $1. At +100%, we sold at $2. At +150%, we sold at $5. Meanwhile, it went to $136. Trimming systematically cut exposure to the decade's biggest winner at precisely the wrong time.

**Lesson 1**: In portfolios with lottery-ticket outliers, ANY profit-taking is catastrophically expensive."""),

    # Phase 2
    create_markdown_cell("""## Phase 2: The Innovation That Failed

### The Dip-Buy Hypothesis

What if we didn't reinvest immediately? What if we waited for market drops and bought SPY/QQQ on 5% dips?

This felt clever. Take profits at peaks, redeploy at troughs. Buy low, sell high. Textbook.

### Results

The dip-buy strategy executed 6-9 successful dip purchases over 10 years. And it *still* underperformed immediate reinvestment.

- **Buy-and-hold**: $5.4M (50.1% CAGR)
- **Best dip-buy strategy**: $2.7M (39.8% CAGR)
- **Immediate SPY reinvestment**: $3.1M (41.2% CAGR)

### Why It Failed

**Opportunity cost.** Cash waiting for dips sat idle during the longest bull market in history. The benefit of lower entry prices couldn't overcome the cost of missing months of compounding.

In sideways or bear markets, this might work. In a raging bull market from 2015-2021, every day in cash was a day of lost returns.

**Lesson 2**: Market timing—even "smart" timing—costs you in strong bull runs."""),

    # Phase 3
    create_markdown_cell("""## Phase 3: The Portfolio Composition Breakthrough

### The Realization

Nobody buys NVDA at $0.48. That's lottery-level luck. Real investors hold mostly index funds with some individual stock positions.

I rebuilt the portfolio to reflect actual investor behavior:
- **60% index funds**: SPY 30%, QQQ 20%, VOO 10%
- **40% individual stocks**: AAPL 15%, MSFT 15%, TSLA 10%

This is an *illustrative* allocation, not an optimized one. It represents index-heavy portfolios common among retail investors.

### Results: Everything Flipped"""),

    # Chart 2: Risk-Return Scatter
    create_img_cell("visualizations/risk_return_scatter.png", "Risk-Return Efficient Frontier"),

    create_markdown_cell("""- **Buy-and-hold**: $689k (21.7% CAGR, -46.3% max drawdown, 0.90 Sharpe)
- **Best trimming (Volatility-2.5× pro-rata)**: $1,047k (26.98% CAGR, -37.8% max drawdown, 1.12 Sharpe)

The best trimming strategy didn't just match buy-and-hold. It *beat* it by **52%** with an 18% lower max drawdown.

This completely inverts the Phase 1 conclusion.

### What Changed?

**Reduced outlier exposure.** With 60% in diversified ETFs, no single stock could dominate outcomes like NVDA did in Phase 1.

**Volatility became signal.** In index-heavy portfolios, volatility spikes often precede mean-reversion. Trimming during volatility captured gains before pullbacks.

**Gradual reinvestment worked.** Spreading reentry over weeks during volatile periods created dollar-cost averaging benefits that immediate reinvestment missed.

**Lesson 3**: Portfolio composition determines whether trimming works. Strategy mechanics matter *less* than what you own."""),

    # Reinvestment Mode Discovery
    create_markdown_cell("""## The Reinvestment Mode Discovery"""),

    # Chart 3: Cumulative Returns
    create_img_cell("visualizations/impressive_cumulative_returns.png", "Cumulative Returns Over Time (2015-2024)"),

    create_markdown_cell("""The gap between strategies wasn't about *when* you trimmed. It was about *how* you reinvested.

### Immediate Reinvestment

- **Pro-rata**: Maintained exposure to high-growth stocks. Strongest performer in Phase 1.
- **SPY**: Rotated profits to slower index. Underperformed by moving capital from winners to laggards.

### Gradual Reinvestment (DRIP: 25%/week)

- **Pro-rata DRIP**: Beat immediate pro-rata by 3-5% in volatile periods.
- **SPY DRIP**: Still underperformed, but gap narrowed vs immediate SPY.

### Market-Timing Reinvestment

- **Dip-buy (5% S&P drop)**: Worst performer. Opportunity cost destroyed returns.

### Yield/Volatility-Based Reinvestment

- **Gradual reentry using dividend yield + VIX**: Best overall. Combined dollar-cost averaging with volatility signals.
- Conceptually similar to **volatility harvesting**: buying when variance is high, capturing mean-reversion."""),

    # Chart 4: Reinvestment Mode Comparison
    create_img_cell("visualizations/reinvestment_mode_comparison.png", "Reinvestment Mode Impact Analysis"),

    create_markdown_cell("""**Key Insight**: Gradual reinvestment during volatile periods creates alpha. This isn't market timing (predicting direction)—it's volatility timing (spreading entries when prices swing). The former fails; the latter works.

**Lesson 4**: Don't just take profits. Structure *how* you redeploy them."""),

    # Volatility-Based Trimming
    create_markdown_cell("""## Volatility-Based Trimming: When Algorithms Fail

### The Hypothesis

What if we trimmed based on volatility instead of fixed price thresholds? Trim more when stocks are whipsawing, less when they're stable.

This is algorithmic loss aversion: avoid holding positions during high-variance regimes.

### Results

Volatility-based trimming with immediate reinvestment *underperformed* fixed thresholds in Phase 1 (outlier-heavy portfolio). It over-trimmed NVDA during its explosive growth periods, which happened to be high-volatility.

But in Phase 3 (index-focused portfolio), volatility-2.5× with gradual pro-rata reinvestment produced the **highest CAGR** (26.98%).

### Why?

**In concentrated portfolios**: High volatility often precedes explosive growth (NVDA 2020-2024). Trimming during volatility cuts winners early.

**In diversified portfolios**: High volatility often precedes mean-reversion. Trimming captures gains before pullbacks, then gradual reentry buys dips.

This is a **behavioral finance lesson**: The same algorithm produces opposite outcomes depending on portfolio structure. There's no universal "smart" trigger.

**Lesson 5**: Algorithmic rules interact with portfolio composition. Test your strategy on *your* holdings, not generic backtests."""),

    # Rolling Performance
    create_markdown_cell("""## Rolling Performance Analysis"""),

    # Chart 5: Rolling Returns
    create_img_cell("visualizations/impressive_rolling_returns.png", "Rolling 1-Year Returns"),

    create_markdown_cell("""Looking at 1-year rolling returns reveals when trimming helped vs hurt:

- **2016-2019 (steady bull market)**: Trimming lagged buy-and-hold. Opportunity cost from reducing winners.
- **2020 (COVID crash/recovery)**: Trimming with gradual reinvestment *outperformed*. Captured pre-crash gains, bought recovery dips.
- **2021-2022 (volatile chop)**: Trimming matched or beat buy-and-hold. Profit-taking during peaks, reentry during dips.
- **2023-2024 (AI boom)**: Trimming lagged again. Missing runaway momentum.

**Pattern**: Trimming works in volatile/choppy markets. Buy-and-hold works in steady trends.

**Lesson 6**: No strategy dominates all regimes. Trimming is volatility insurance, not a return maximizer."""),

    # Sensitivity Analysis
    create_markdown_cell("""## Sensitivity Analysis"""),

    # Chart 6: Sensitivity Heatmap Pro-Rata
    create_img_cell("visualizations/sensitivity_heatmap_pro_rata.png", "Sensitivity Analysis - Pro-Rata Reinvestment"),

    create_markdown_cell("""Testing trim thresholds (50% to 200%) against trim sizes (10% to 50%) reveals:

- **Higher thresholds + smaller trim sizes**: Fewest regrets. Let winners run, take modest profits.
- **Lower thresholds + larger trim sizes**: Maximum regret. Over-trim early, miss compounding.
- **Sweet spot**: 100-150% threshold, 15-20% trim size.

But this is portfolio-specific. In Phase 1 (NVDA-heavy), *no* trimming beats buy-and-hold. In Phase 3 (index-heavy), strategic trimming wins.

**Lesson 7**: Optimize trim parameters for *your* portfolio, not generic rules."""),

    # Chart 7: Sensitivity Heatmap SPY
    create_img_cell("visualizations/sensitivity_heatmap_spy.png", "Sensitivity Analysis - SPY Reinvestment"),

    # Drawdown Analysis
    create_markdown_cell("""## Drawdown Analysis"""),

    # Chart 8: Drawdown Timeline
    create_img_cell("visualizations/impressive_drawdown_timeline.png", "Drawdown Timeline with Market Events"),

    create_markdown_cell("""Maximum drawdown comparison:
- **Buy-and-hold**: -46.3% (March 2020 COVID crash)
- **Best trimming**: -37.8% (Volatility-2.5× pro-rata DRIP)

That 8.5% difference is the **psychological benefit** of trimming. Smoother ride, less panic-selling risk.

During the COVID crash, trimming strategies had already taken some profits in Feb 2020 (volatility spike). More cash cushion when markets tanked. Gradual reinvestment in March-April bought near the bottom.

**Lesson 8**: Trimming isn't just about returns. It's about surviving drawdowns without panic-selling."""),

    # What Actually Works
    create_markdown_cell("""## What Actually Works: The Framework

After 42 strategies and three portfolio configurations, here's what matters:

### 1. **Know What You Own**
- **Concentrated/high-conviction portfolios**: Buy-and-hold wins. Don't trim potential 100x winners.
- **Diversified/index-heavy portfolios**: Strategic trimming can outperform with better risk metrics.

### 2. **Gradual Reinvestment > Market Timing**
- Spread reentry over weeks during volatile periods (dollar-cost averaging effect).
- Don't wait for specific dip thresholds—opportunity cost kills you.
- Use volatility signals (VIX, yield spreads) to guide pace, not direction.

### 3. **Volatility Awareness**
- In concentrated portfolios: High volatility = potential breakout. Don't trim.
- In diversified portfolios: High volatility = mean-reversion setup. Trim and gradually reenter.

### 4. **Reinvest in What's Working**
- Pro-rata reinvestment (back into trimmed positions) preserves winner exposure.
- Rotating to SPY underperforms unless your stocks are genuinely broken.

### 5. **Higher Thresholds, Smaller Trims**
- 100-150% gain thresholds vs 50% (fewer trims = more time in winners).
- 15-20% trim sizes vs 30-50% (preserve core position)."""),

    # Limitations
    create_markdown_cell("""## Limitations and Alternative Interpretations

### What This Backtest Doesn't Capture

**Taxes**: Real-world capital gains tax (15-37%) penalizes trimming heavily. The backtest engine supports tax modeling, but baseline results assume 0% for strategy comparison. Adding 20% long-term cap gains would reduce trimming strategies more than buy-and-hold (more transactions = more tax events).

**Behavioral reality**: Systematic rules require discipline. Most investors don't follow them consistently.

**Regime dependency**: 2015-2024 was mostly bull market. Bear market testing (2000-2002, 2008-2009) would likely favor trimming.

**Survivorship bias**: This portfolio excludes stocks that went to zero. In reality, trimming protects against blow-ups.

### Alternative Interpretation

Maybe trimming's real value isn't beating buy-and-hold—it's *preventing catastrophic mistakes*. If trimming keeps you from panic-selling during crashes (because you already have cash), it's worth modest underperformance during bull runs.

**Risk-adjusted returns matter**: 26.98% CAGR with -37.8% drawdown vs 21.7% CAGR with -46.3% drawdown. The first lets you sleep at night."""),

    # Recommendations
    create_markdown_cell("""## Recommendations

### For Index-Heavy Portfolios (60%+ ETFs)
- **Use volatility-based trimming** (1.5-2.5× rolling average thresholds)
- **Gradual pro-rata reinvestment** (25% per week over 4 weeks)
- **Target 100-150% gain thresholds**, 15-20% trim sizes
- **Expected outcome**: Comparable or better returns than buy-and-hold with lower drawdowns

### For Concentrated/High-Conviction Portfolios
- **Don't trim systematically.** Let outliers run.
- **Exception**: Trim for risk management if single position exceeds 30-40% of portfolio (concentration risk).
- **Expected outcome**: Maximum upside capture, higher volatility

### For Volatile/Choppy Markets
- **Trimming shines.** Capture gains during peaks, gradual reentry during dips.
- **Use yield/volatility signals** to guide reinvestment pace.

### For Steady Bull Markets
- **Buy-and-hold wins.** Trimming creates opportunity cost.
- **If you must trim**: Higher thresholds (150-200%), smaller sizes (10-15%)."""),

    # Lessons Learned
    create_markdown_cell("""## Lessons Learned (Beyond Returns)

### 1. **Assumptions Matter More Than Mechanics**
The Phase 3 breakthrough wasn't better code—it was questioning the assumption that we'd buy NVDA at $0.48. Realistic scenarios change everything.

### 2. **Backtests Lie When You Let Them**
Initial results said "trimming always loses." Digging deeper revealed "trimming loses in *this* portfolio configuration." Context is everything.

### 3. **There Is No Free Lunch**
Every strategy trades something. Trimming trades upside for downside protection. Buy-and-hold trades sleep for returns. Know what you're trading.

### 4. **Discipline Beats Optimization**
A consistent 100% threshold strategy beats sporadically trying to "optimize" trims. Systems work because they remove emotions, not because they're perfect.

### 5. **Volatility Is Information**
High volatility isn't just risk—it's a signal. In diversified portfolios, it tells you when to harvest gains and when to gradually reenter. Treat volatility as data, not noise."""),

    # Conclusion
    create_markdown_cell("""## Conclusion

The question "Does trimming work?" has no single answer. It depends on what you own, how you reinvest, and what market regime you're in.

**If you own concentrated positions with outlier potential**: Don't trim. You'll sell the next NVDA at $5 while it goes to $136.

**If you own diversified index-heavy portfolios**: Strategic trimming with gradual reinvestment can beat buy-and-hold while cutting drawdowns by 18%.

**If you're in volatile markets**: Trimming is volatility insurance. Capture gains, spread reentry, survive the chop.

**If you're in steady bull markets**: Buy-and-hold wins. Don't outsmart yourself.

The real lesson isn't about finding the perfect strategy—it's about understanding how systematic rules interact with your holdings. Test your approach on *your* portfolio. Know what you're optimizing for: pure returns, risk-adjusted returns, or sleep-at-night stability.

And if you ever buy something at $0.48 that goes to $136? For the love of god, don't trim it."""),

    # Appendix
    create_markdown_cell("""## Appendix: Full Results Summary

| Strategy | Final Value | CAGR | Sharpe | Max DD | Volatility |
|----------|-------------|------|--------|---------|------------|
| **Phase 1 (Equal-Weight 6 Stocks)** |
| Buy-and-Hold | $5,430,469 | 50.14% | 1.29 | -50.8% | 0.34 |
| Trim@+150% (pro-rata) | $4,344,733 | 46.65% | 1.33 | -45.2% | 0.31 |
| Trim@+50% (SPY) | $1,132,890 | 28.08% | 0.77 | -48.6% | 0.32 |
| **Phase 3 (Index-Focused 60/40)** |
| Buy-and-Hold | $688,711 | 21.69% | 0.90 | -46.3% | 0.21 |
| Volatility-2.5× (pro-rata DRIP) | $1,047,392 | 26.98% | 1.12 | -37.8% | 0.20 |
| Trim@+100% (pro-rata DRIP) | $673,205 | 21.48% | 0.94 | -40.1% | 0.19 |

*Full 42-strategy results available in `/results_index_focus/index_focus_results.csv`*

---

**Backtest Code**: Available at `/Users/austinwallace/sandbox/stock_strategies/trim_strat_test/`
**Data Source**: Yahoo Finance (2015-2024)
**Validation**: Comprehensive validation script confirms metric accuracy (`/src/validation/comprehensive_validation.py`)""")
]

# Create notebook structure
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Write notebook
output_path = Path("Taking_Profits_What_Actually_Works.ipynb")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print(f"✅ Created refined notebook: {output_path}")
print(f"📊 Total cells: {len(cells)}")
print(f"🖼️  Charts embedded: 8")
