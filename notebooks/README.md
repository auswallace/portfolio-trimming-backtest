# Notebooks Directory

## 📖 Main Research Report

**The complete research report is in the root [`README.md`](../README.md)** - This renders perfectly on GitHub and contains:
- Complete analysis narrative
- All 19 visualizations (embedded and viewable)
- Results tables for all 42 strategies
- Methodology, findings, and insights
- Professional presentation

**→ [Read the Main Report](../README.md)**

---

## Jupyter Notebooks (Code Structure Only)

The notebooks in this directory contain code structure but **have not been executed**. They were used to organize the analysis workflow but do not contain output.

**`COMPREHENSIVE_BACKTEST_REPORT.ipynb`** - Analysis code structure

- **Strategies**: 42 total (5 trim types × 6 reinvestment modes + baseline)
- **Updates**: UPDATE 1-3 complete
  - UPDATE 1: Momentum & volatility strategies, advanced metrics
  - UPDATE 2: Comprehensive notebook with 8+ charts
  - UPDATE 3: Cost/tax modeling, validation, fact-checking
- **Status**: Code cells present, outputs not executed
- **Note**: All results, charts, and analysis are available in root README.md and `/visualizations/` directory

---

## Archived Notebooks (Historical Reference)

See `archive/` directory for older versions from Phase 1-4:

- **`RESEARCH_REPORT.ipynb`** - Phase 4 (DC voice transformation)
- **`RESEARCH_REPORT_CONDENSED.ipynb`** - Phase 4 condensed version (~1,800 words)
- **`portfolio_trimming_analysis.ipynb`** - Original Phase 1/2 analysis (NVDA-dominated portfolio)

These are preserved for historical reference but are **superseded** by the comprehensive notebook.

---

## Development History

1. **Phase 1**: NVDA-dominated portfolio (equal-weight 6 stocks) - Buy-and-hold crushed trimming
2. **Phase 2**: Dip-buy innovation testing - Opportunity cost > timing benefit
3. **Phase 3**: Realistic index-focused portfolio (60/40 split) - Trimming nearly matched buy-and-hold
4. **Phase 4**: DC voice transformation + initial fact-checking
5. **Phase 5 (UPDATE 3)**: Cost/tax modeling, comprehensive validation, extensive fact-checking

---

## Next Steps

- **Test with costs**: Enable toggles (0.1% + 20% tax) and re-run backtest
- **Export**: Convert to PDF/HTML for sharing
- **Publish**: Share on GitHub, blog, or portfolio
- **Optimize**: Test 10% trim size (sensitivity analysis suggests it's better than 20%)
