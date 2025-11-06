# Portfolio Trimming Strategy Analysis

A comprehensive quantitative analysis comparing **buy-and-hold** vs **position trimming** strategies for a stock portfolio.

## Overview

This project simulates whether implementing a trimming strategy (taking partial profits at defined gain thresholds) would outperform a buy-and-hold approach over a 10-year backtest period.

### What Gets Tested

**Strategies:**
- **Buy-and-Hold Baseline** - No selling, hold forever
- **Trim @ +50%** - Sell 20% when position gains 50%
- **Trim @ +100%** - Sell 20% when position doubles
- **Trim @ +150%** - Sell 20% when position is up 150%

**Reinvestment Modes** (for each trim strategy):
1. **Pro-rata** - Redistribute proceeds across all holdings proportionally
2. **SPY** - Invest proceeds into S&P 500 ETF
3. **Cash** - Hold proceeds as cash (0% return)

**Total:** 10 strategies tested (1 baseline + 9 trim variations)

## Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Setup

1. **Clone or navigate to this directory:**
```bash
cd /path/to/trim_strat_test
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Launch Jupyter:**
```bash
jupyter notebook portfolio_trimming_analysis.ipynb
```

## Usage

### Quick Start

1. Open `portfolio_trimming_analysis.ipynb` in Jupyter
2. Run all cells sequentially (Kernel → Restart & Run All)
3. Review results in the final summary section

### Customization

The notebook is designed to be easily customizable. Key configuration variables are in **Step 2**:

```python
# Modify these to test different scenarios:
PORTFOLIO = {...}  # Your holdings
START_DATE = '2015-01-01'  # Backtest start
TRIM_THRESHOLDS = [0.50, 1.00, 1.50]  # Gain levels
TRIM_PERCENTAGE = 0.20  # How much to sell (20%)
INITIAL_CASH = 100000  # Starting capital
```

### Interpreting Results

The notebook produces:

1. **Performance Comparison Table** - All strategies ranked by final value
2. **Portfolio Value Chart** - Growth over time visualization
3. **Drawdown Analysis** - Risk/volatility comparison
4. **Risk-Return Scatter** - Efficient frontier view
5. **Performance Heatmap** - Color-coded metrics overview
6. **Summary Analysis** - Natural language interpretation

## Key Metrics Explained

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **Final Value** | Portfolio value at end | Higher = more money |
| **CAGR** | Compound Annual Growth Rate | Higher = faster growth |
| **Sharpe Ratio** | Return per unit of risk | Higher = better risk-adjusted returns (>1.0 is good) |
| **Sortino Ratio** | Like Sharpe, but only penalizes downside | Higher = better |
| **Max Drawdown** | Largest peak-to-trough decline | Lower = less painful journey |
| **Volatility** | Standard deviation of returns | Lower = more stable |

## Portfolio Details

Default portfolio (from your current holdings):

| Ticker | Shares |
|--------|--------|
| AAPL   | 33     |
| ATXRF  | 1355   |
| BITF   | 250    |
| COIN   | 15     |
| IBIT   | 22     |
| MSFT   | 5      |
| MSTR   | 25     |
| NET    | 15     |
| NVDA   | 35     |
| PLTR   | 12     |
| QQQ    | 25     |
| SPY    | 7      |
| TSLA   | 3      |
| UNH    | 7      |
| VOO    | 13     |
| XYZ    | 12     |

**Note:** Tickers without 10 years of history (e.g., IBIT launched 2024) are automatically filtered out and excluded from the backtest.

## Technical Details

### Data Source
- **yfinance** - Historical stock prices from Yahoo Finance
- **Adjusted close prices** - Accounts for splits and dividends
- **Daily frequency** - ~2,500 trading days over 10 years

### Backtesting Framework
- **VectorBT** - Professional portfolio simulation library
- **Realistic fees** - 0.1% trading costs included
- **Proper position tracking** - Accurate share count and cash management

### Limitations & Considerations

1. **No tax modeling** - Real taxes would reduce trimming strategy returns significantly
2. **Past performance** - Backtests show what worked historically, not what will work
3. **Survivorship bias** - Assumes you held positions that may have been sold earlier
4. **Transaction costs** - Only basic 0.1% fees; doesn't account for slippage or market impact
5. **Psychological factors** - Assumes perfect discipline (real humans struggle to stick to plans)

## Expected Runtime

- **Data download:** 30-60 seconds (depends on internet speed)
- **Strategy backtesting:** 2-5 minutes (depends on CPU)
- **Visualization generation:** 10-20 seconds
- **Total:** ~5 minutes for full notebook execution

## Output Files

After running the notebook:
- `trimming_strategy_results.csv` - Exportable performance metrics for all strategies

## Troubleshooting

### Common Issues

**"No module named 'vectorbt'"**
```bash
pip install vectorbt
```

**"Unable to download data for XYZ"**
- XYZ appears to be invalid ticker
- Notebook will auto-filter and continue with valid tickers

**VectorBT installation fails**
- Try: `pip install --upgrade pip`
- Or use conda: `conda install -c conda-forge vectorbt`

**Plots not showing**
- Ensure running in Jupyter (not plain Python)
- Try: `%matplotlib inline` in first cell

## Extending the Analysis

### Add More Trim Thresholds
```python
TRIM_THRESHOLDS = [0.25, 0.50, 0.75, 1.00, 1.50, 2.00]
```

### Change Trim Size
```python
TRIM_PERCENTAGE = 0.10  # Sell 10% instead of 20%
```

### Test Different Time Periods
```python
START_DATE = '2010-01-01'  # Longer backtest
END_DATE = '2020-12-31'    # Exclude COVID recovery
```

### Add Tax Modeling
Modify the `TrimStrategy` class to deduct capital gains taxes on each trim event.

## References

- **VectorBT Documentation:** https://vectorbt.dev/
- **yfinance Documentation:** https://pypi.org/project/yfinance/
- **Portfolio Theory:** Modern Portfolio Theory (Markowitz, 1952)

## License

This notebook is for educational and personal use only. Not financial advice.

---

**Questions or Issues?** Review the notebook's markdown cells for detailed explanations of each step.
