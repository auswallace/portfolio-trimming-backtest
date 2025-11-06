# Portfolio Trimming vs Buy-and-Hold: A $5M Quantitative Study

**Does taking profits beat holding forever? I backtested 13 strategies across 10 years to find out.**

---

## 🎯 Key Findings (TL;DR)

**The answer: IT DEPENDS ON WHAT YOU OWN.**

![Performance Comparison](visualizations/performance_waterfall.png)
*13 strategies tested across 3 different portfolio compositions. Results ranged from $670k to $5.4M.*

### Finding #1: In NVDA-Heavy Portfolios, Buy-and-Hold Crushed Trimming

- **Buy-and-Hold:** $5,430,469 final value (50.14% CAGR)
- **Best Trimming:** $4,344,733 (46.65% CAGR)
- **Verdict:** Trimming cost $1.1M (20% worse)

**Why:** NVDA gained 28,057% ($0.48 → $136). Every trim sold at $1-$5 while it went to $136. Trimming killed the decade's biggest winner.

### Finding #2: In Index-Heavy Portfolios, Trimming Nearly Matched Buy-and-Hold

![Risk-Return Efficient Frontier](visualizations/risk_return_frontier.png)
*When portfolios are mostly index funds, trimming offers better risk-adjusted returns for minimal return sacrifice.*

- **Buy-and-Hold:** $688,711 (21.69% CAGR, 0.90 Sharpe, -46.3% drawdown)
- **Best Trimming:** $670,744 (21.36% CAGR, 0.94 Sharpe, -40.8% drawdown)
- **Difference:** Only $18k (2.6%) with BETTER Sharpe ratio and 6% LOWER drawdowns

**The Insight:** Portfolio composition matters MORE than strategy choice. With outlier winners (NVDA), trimming is catastrophic. With index-heavy allocations, trimming is viable.

### Finding #3: Market Timing Fails Even When You Time It Correctly

![Drawdown Timeline](visualizations/drawdown_timeline.png)
*Testing a "smart" dip-buying strategy: wait for 5% S&P drops, buy SPY/QQQ on sale.*

- **Result:** Still underperformed immediate reinvestment
- **Why:** Opportunity cost (cash drag in bull market) > timing benefit (lower entry prices)
- **Lesson:** Time in market > timing the market (even when you get the timing right)

### Finding #4: Higher Trim Thresholds Preserve Winners

| Strategy | Final Value | CAGR | Sharpe | Num Trims |
|----------|-------------|------|--------|-----------|
| Trim @ +150% | $670,744 | 21.36% | 0.94 | 10 |
| Trim @ +100% | $670,503 | 21.36% | 0.94 | 14 |
| Trim @ +50% | $655,032 | 21.16% | 0.92 | 23 |

**Pattern:** Fewer trims (higher thresholds) = more time in winners = better performance

### Finding #5: Pro-Rata Reinvestment Dominates

![Strategy Heatmap](visualizations/strategy_heatmap.png)
*Reinvesting trim proceeds back into the same portfolio (pro-rata) consistently outperformed rotating to SPY or holding cash.*

**Why:** Maintains exposure to high-growth stocks instead of rotating profits to slower index funds.

---

## 📊 The Three Research Phases

### Phase 1: The NVDA Trap (Equal-Weight Stocks)
**Portfolio:** AAPL, MSFT, NVDA, TSLA, SPY, QQQ (16.67% each)
**Initial Capital:** $100,000
**Period:** 2015-2024 (2,477 trading days)
**Conclusion:** Buy-and-hold won by $1.1M due to NVDA's 28,057% outlier gain

### Phase 2: The Dip-Buy Innovation (Market Timing Test)
**Strategy:** Trim at gains, wait for 5% S&P drops, buy SPY/QQQ on dips
**Execution:** 6-9 successful dip-buys over 10 years
**Conclusion:** Still underperformed immediate reinvestment (cash drag > timing benefit)

### Phase 3: The Realistic Scenario ⭐ (The Breakthrough)
**Portfolio:** 60% index funds (SPY/QQQ/VOO) + 40% stocks (AAPL/MSFT/TSLA)
**Insight:** "Nobody actually bought NVDA at $0.48 - that's lottery-level luck"
**Conclusion:** Trimming MATCHED buy-and-hold (2.6% difference) with better risk metrics

**The Flip:** Removing the NVDA outlier and using realistic allocations completely reversed the Phase 1 conclusion.

---

## 💡 What This Means for Investors

### If Your Portfolio is Index-Heavy (60%+ SPY/QQQ/VOO):
✅ **Trimming is viable** - You give up 0.33% CAGR but get:
- Better Sharpe ratio (more return per unit of risk)
- 6% lower max drawdowns (less pain in crashes)
- Smoother ride (lower volatility)

**Good for:** Risk-averse investors, retirees, those who need to sleep at night

### If Your Portfolio Has Potential 100x Winners (Concentrated Stock Picks):
❌ **Don't trim** - You'll sell your NVDA at $5 while it goes to $136
- Let winners run
- Accept higher volatility and drawdowns
- Maximize absolute returns

**Good for:** Growth-focused investors, long time horizons, high risk tolerance

### Universal Lessons:
1. **Portfolio composition matters MORE than strategy choice**
2. **If you must trim, use high thresholds** (+150% > +100% > +50%)
3. **Reinvest pro-rata** (maintain allocation vs rotating to index)
4. **Market timing is hard even when correct** (dip-buying failed)

---

## 🛠️ How I Built This (Skills Demonstrated)

### 1. Quantitative Analysis & Domain Knowledge

**Custom Backtesting Engine** - Built from scratch in Python (not a library wrapper) because I needed:
- Full control over cost basis reset logic (allows re-triggering same thresholds)
- Custom reinvestment modes (pro-rata, SPY-only, cash, dip-buy)
- Transparent metric calculations (CAGR, Sharpe, Sortino, max drawdown)

**Key Design Decisions:**
```python
# Cost basis reset after trim (my innovation)
new_cost_basis = current_price * 1.05  # Reset to current + 5%
# Without this, you only trim once (unrealistic)

# Trading-day basis (252 days/year, not calendar)
trading_years = total_days / 252  # More accurate CAGR

# Four reinvestment modes tested:
# 1. Pro-rata: Maintain allocation (keeps exposure to winners)
# 2. SPY-only: Rotate to S&P 500 (conservative)
# 3. Cash: Hold proceeds (timing test)
# 4. Dip-buy: Wait for 5% S&P drops (smart timing)
```

**Why Custom vs Library:** Backtrader/Zipline optimize for speed. I optimized for **transparency and educational value**. Every calculation is explicit and verifiable.

### 2. Research Methodology & Critical Thinking

**Multi-Phase Hypothesis Testing:**

**Phase 1 Result:** "Trimming loses by $1.1M"
**My Reaction:** "Wait, why? This doesn't match my intuition."
**My Analysis:** Dug into trade logs, found NVDA contributed $4.5M to buy-and-hold. Identified outlier distortion.

**Phase 2 Hypothesis:** "Maybe the problem is immediate reinvestment. Let's wait for dips."
**Implementation:** Built dip-detection logic (5% S&P drop from recent high)
**Result:** Still underperformed
**My Analysis:** Opportunity cost (cash drag) exceeded timing benefit in bull market

**Phase 3 Insight:** "Nobody actually bought NVDA at $0.48 - that's lottery luck. Real portfolios are index-heavy."
**Redesign:** 60/40 index/stock allocation (SPY 30%, QQQ 20%, VOO 10%, AAPL 15%, MSFT 15%, TSLA 10%)
**Result:** Conclusions completely flipped - trimming viable
**Breakthrough:** **Assumptions matter more than code**

This demonstrates:
- Identifying confounding variables (NVDA outlier)
- Questioning initial assumptions (equal-weight stocks)
- Iterating when results don't make sense
- Domain knowledge guiding research direction

### 3. Data Engineering & Technical Implementation

**Data Pipeline:**
1. **Downloaded** real Yahoo Finance data (2015-2024 daily OHLC)
2. **Validated** - Checked for missing dates, handled stock splits, aligned time series
3. **Cached** locally - Avoid rate limits, enable reproducibility
4. **Processed** - pandas DataFrames, calculated daily returns, vectorized operations
5. **Backtested** - Day-by-day simulation across 13 strategies (3 thresholds × 4 modes + baseline)
6. **Exported** - CSV metrics + detailed trade logs

**Tech Stack:**
- Python 3.9+ (pandas, numpy)
- yfinance API (market data)
- matplotlib/seaborn (300 DPI visualizations)
- Jupyter notebooks (executable research)

**Why Real Data vs Synthetic:** Synthetic data would miss real market behavior (NVDA outlier, 2020 COVID crash, recovery dynamics). Results wouldn't be credible.

### 4. Visualization & Communication

**7 Professional Charts Generated:**
1. **Performance Waterfall** - All 13 strategies ranked by returns
2. **Risk-Return Efficient Frontier** - Volatility vs CAGR scatter
3. **Drawdown Timeline** - With market event annotations
4. **Strategy Performance Heatmap** - Metrics across strategies
5. **Rolling Returns Comparison** - 1-year rolling windows
6. **Multi-Metric Radar Chart** - CAGR, Sharpe, MDD, Sortino
7. **Cumulative Returns Race** - Performance evolution over time

**Design Standards:**
- 300 DPI resolution (publication-quality)
- Colorblind-friendly palettes
- Clear titles, axis labels, legends
- Professional grid styling

**Data Storytelling:** Structured as 3-phase narrative showing evolution of thinking (failed hypotheses → breakthrough insights)

### 5. AI Engineering (Force Multiplier, Not Replacement)

After completing the analysis, I built a **4-agent pipeline** to automate report generation:

```
Raw CSV Data
    ↓
[Agent 1: Technical Writer]
    → Generates Jupyter notebook with 7 embedded charts
    → Writes methodology, results, conclusions sections
    ↓
[Agent 2: Voice Transformer]
    → Constraint: Must preserve 100% of numbers/data
    → Converts formal academic tone → conversational style
    ↓
[Agent 3: Fact-Checker]
    → Independently recalculates all metrics from CSVs
    → Questions assumptions ("realistic portfolio" claim)
    → Found 8 issues (CAGR discrepancies, unjustified language)
    ↓
[Agent 4: Revision Editor]
    → Applies specific corrections surgically
    → Output: Publication-ready notebook ✅
```

**Why This Matters:**

**Not:** "I used AI to do my analysis"
**Yes:** "I used AI to automate tedious report formatting so I could focus on insight generation"

**The Split:**
- **I did:** Hypothesis generation, assumption testing, confounding variable identification, metric selection, algorithm design
- **AI did:** Report structuring, chart formatting, tone transformation, systematic validation

**Result:** 2 days of manual work → 30 minutes of supervised automation. I focus on **high-value analytical work**, AI handles **low-value formatting work**.

**Engineering Principles Applied:**
- **Separation of concerns** - Each agent has ONE job
- **Constraint design** - "Preserve 100% of data" prevents hallucination
- **Independent validation** - Fact-checker catches errors
- **Version control** - Agent prompts stored in `.claude/agents/`

---

## 📈 Complete Results Table

### Phase 3: Realistic Portfolio (60% Index / 40% Stocks)

| Strategy | Final Value | CAGR | Sharpe | Sortino | Max DD | Volatility | Trades |
|----------|-------------|------|--------|---------|---------|-----------|---------|
| **Buy-and-Hold** | **$688,711** | **21.69%** | 0.90 | 1.28 | **-46.3%** | 21.34% | 0 |
| Trim@+150% (pro-rata) | $670,744 | 21.36% | **0.94** | **1.32** | -40.8% | **20.89%** | 10 |
| Trim@+100% (pro-rata) | $670,503 | 21.36% | **0.94** | **1.32** | **-40.8%** | **20.89%** | 14 |
| Trim@+50% (pro-rata) | $655,032 | 21.16% | **0.92** | 1.29 | -41.9% | 21.11% | 23 |
| Trim@+150% (SPY) | $640,449 | 20.85% | 0.89 | 1.25 | -42.5% | 21.54% | 10 |
| Trim@+100% (SPY) | $619,449 | 20.49% | 0.88 | 1.23 | -42.9% | 21.46% | 14 |
| Trim@+50% (SPY) | $576,447 | 19.59% | 0.84 | 1.17 | -44.0% | 21.48% | 23 |

**Bold = Best in category**

**Key Patterns:**
- Pro-rata reinvestment > SPY reinvestment (maintains growth exposure)
- Higher thresholds > Lower thresholds (fewer trims preserve winners)
- Trimming beats B&H on risk metrics (Sharpe, Sortino, drawdown) while matching returns

---

## 🚀 Run It Yourself

### Quick Start
```bash
git clone https://github.com/yourusername/portfolio-trimming-backtest
cd trim_strat_test
pip install -r requirements.txt

# Run Phase 3 backtest (realistic portfolio)
python src/backtest/run_backtest_index_focus.py

# View research report
jupyter notebook RESEARCH_REPORT_FINAL_PUBLICATION_READY.ipynb
```

### Prerequisites
- Python 3.9+
- pandas, numpy, matplotlib, seaborn, yfinance, jupyter

### Output Files
- `results_index_focus/index_focus_results.csv` - 13 strategy metrics
- `results_index_focus/index_focus_output.txt` - Detailed trade logs
- `visualizations/*.png` - 7 professional charts (300 DPI)

---

## 📁 Project Structure

```
trim_strat_test/
├── src/
│   ├── backtest/
│   │   ├── run_backtest_index_focus.py    # Phase 3: Realistic ⭐
│   │   ├── run_backtest_manual_data.py    # Phase 1: NVDA-heavy
│   │   └── run_backtest_with_dip.py       # Phase 2: Dip-buy
│   ├── visualization/
│   │   └── generate_impressive_visualizations.py
│   └── utils/
│       └── download_with_cache.py
│
├── .claude/agents/                        # AI automation pipeline
│   ├── research-report-generator.md       # Technical writer
│   ├── personal-tone-matcher.md           # Voice transformer
│   ├── finance-fact-checker.md            # QA validator
│   └── assumption-revision-agent.md       # Editor
│
├── results_index_focus/                   # Backtest outputs
├── visualizations/                        # Charts (300 DPI)
└── RESEARCH_REPORT_FINAL_PUBLICATION_READY.ipynb  # Final report ✅
```

---

## 🎓 What I Learned

### About Investing
- Portfolio composition matters MORE than strategy choice
- Outlier winners dominate returns (NVDA was 83% of Phase 1 gains)
- Risk-adjusted returns can justify lower absolute returns
- Market timing is hard even when executed correctly

### About Research
- Assumptions must be challenged - "equal-weight stocks" led to wrong conclusion
- Multi-phase testing reveals nuance - single backtest would have missed key insight
- Confounding variables hide truths - NVDA outlier masked real trimming comparison
- Domain knowledge guides iteration - knowing "nobody buys at $0.48" drove breakthrough

### About AI Engineering
- Specialization > generalization (4 focused agents > 1 general agent)
- Constraints prevent hallucination ("preserve 100% of data" rule critical)
- Independent validation catches errors (fact-checker found 8 issues)
- Automation amplifies productivity (2 days → 30 minutes with oversight)

---

## 🔮 Future Research Directions

**High Priority:**
- **Tax modeling** - Deduct 15-20% capital gains tax from trims
- **Bear market testing** - Validate during 2018, 2020, 2022 corrections
- **Dynamic thresholds** - Trim based on P/E ratios vs fixed gains

**Medium Priority:**
- **Sector analysis** - Does trimming work better for utilities vs tech?
- **Position sizing** - Test 10%, 30%, 50% trim sizes (vs fixed 20%)
- **Different portfolios** - Value stocks, dividend stocks, bonds

---

## 🏆 Why This Project Stands Out

Most portfolio projects are **one-dimensional**: "I built a model" or "I analyzed data."

This project demonstrates:

✅ **Quantitative rigor** - Custom backtesting engine, 13 strategies tested, real market data
✅ **Critical thinking** - Identified confounding variables, questioned assumptions, iterated approach
✅ **Domain expertise** - Portfolio theory, risk metrics, market mechanics, behavioral finance
✅ **Research methodology** - Multi-phase hypothesis testing, alternative hypothesis exploration
✅ **Technical depth** - Algorithm design, vectorized operations, metric calculations
✅ **AI engineering** - Agent architecture, constraint design, quality control automation
✅ **Communication** - Professional visualizations, clear storytelling, actionable insights
✅ **Intellectual honesty** - Showed failed hypotheses (dip-buying), not just successes

**This isn't "I used AI to do my work."**
**This is "I used AI to amplify my analytical capabilities 10x."**

---

## 👨‍💻 Author

**Austin Wallace**
[LinkedIn](#) | [Portfolio](#) | [Email](mailto:your-email)

*Data analyst building expertise in quantitative finance and research methodology. This project showcases skills in statistical analysis, Python programming, and AI-powered automation. Open to opportunities in data science, quantitative research, financial analysis, or AI/ML engineering.*

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Market data: Yahoo Finance (yfinance)
- Visualization: matplotlib, seaborn
- AI: Anthropic Claude Sonnet 4.5
- Inspired by quant finance community discussions

---

**⭐ If you found this research valuable, please star the repo!**

**📊 [Read the full research report →](RESEARCH_REPORT_FINAL_PUBLICATION_READY.ipynb)**

**💬 Questions? Open an issue or reach out!**
