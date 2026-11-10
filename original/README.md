# An earlier version of this project

These files are the first version of this project, from 2025. They are kept for reference and are not changed.

- `run_backtest_index_focus.py`: the first engine.
- `Taking_Profits_What_Actually_Works.md`: the first report. Its charts are not in this folder. They are in the git history.
- `FACT_CHECK_REPORT_DC_VOICE.md`: an AI review of that report.
- `README_original.md`: the first front page.

Do not rely on the conclusions or the recommendations in these files. The first version tested one portfolio, and the main README shows why that is not enough.

## Known errors in the first engine

The current engine (`src/engine.py`) corrects three errors. `src/audit.py` measures their effect.

1. **Cash was counted on days when it did not exist.** For rules that hold cash after a trim, the engine added the final cash balance to every day. Final values were right. The Sharpe ratio and the drawdown of 28 of the 42 rules can be wrong.

   | Rule | Sharpe, first engine | Sharpe, corrected | Worst drawdown, first engine | Worst drawdown, corrected |
   |---|---|---|---|---|
   | Trim at +50%, hold cash | 0.48 | 0.98 | -24.7% | -26.1% |
   | Trim at +100%, hold cash | 0.61 | 0.96 | -30.0% | -32.8% |
   | Volatility-2.5x, hold cash until calm | 0.78 | 0.87 | -59.7% | -44.4% |

2. **The Sharpe ratio used a 0% risk-free rate.** The report said 2%. With 2%, buy-and-hold scores 0.82 and Volatility-2.5x scores 0.80 on the six-holding portfolio.

3. **One rule set a 4% interest rate for its cash and did not use it.**
