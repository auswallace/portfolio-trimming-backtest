#!/usr/bin/env python
"""
Portfolio Trimming Strategy Backtest
Standalone script version for execution and validation
"""

# Core libraries
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import os
import json
warnings.filterwarnings('ignore')

# Backtesting framework
import vectorbt as vbt

print("="*80)
print("PORTFOLIO TRIMMING STRATEGY BACKTEST")
print("="*80)
print(f"\nVectorBT version: {vbt.__version__}")

# ============================================================================
# CONFIGURATION
# ============================================================================

PORTFOLIO = {
    'AAPL': 33,
    'ATXRF': 1355,
    'BITF': 250,
    'COIN': 15,
    'IBIT': 22,
    'MSFT': 5,
    'MSTR': 25,
    'NET': 15,
    'NVDA': 35,
    'PLTR': 12,
    'QQQ': 25,
    'SPY': 7,
    'TSLA': 3,
    'UNH': 7,
    'VOO': 13,
    'XYZ': 12
}

START_DATE = '2015-01-01'
END_DATE = datetime.now().strftime('%Y-%m-%d')
INITIAL_CASH = 100000
TRIM_THRESHOLDS = [0.50, 1.00, 1.50]
TRIM_PERCENTAGE = 0.20
REINVEST_MODES = ['pro_rata', 'spy', 'cash']

print(f"\nPortfolio Configuration:")
print(f"  Tickers: {len(PORTFOLIO)}")
print(f"  Period: {START_DATE} to {END_DATE}")
print(f"  Initial Capital: ${INITIAL_CASH:,}")
print(f"  Trim Thresholds: {[f'+{int(t*100)}%' for t in TRIM_THRESHOLDS]}")
print(f"  Trim Size: {int(TRIM_PERCENTAGE*100)}% of position")

# ============================================================================
# DATA DOWNLOAD
# ============================================================================

def download_data(tickers, start_date, end_date):
    import time
    print(f"\n📊 Downloading data for {len(tickers)} tickers...")
    print(f"Period: {start_date} to {end_date}\n")

    # Download one ticker at a time to avoid rate limits
    all_data = {}
    failed_tickers = []

    for i, ticker in enumerate(tickers):
        print(f"  Downloading {ticker} ({i+1}/{len(tickers)})...", end='')
        try:
            ticker_data = yf.download(
                tickers=ticker,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True
            )

            if not ticker_data.empty:
                all_data[ticker] = ticker_data['Close']
                print(" ✓")
            else:
                failed_tickers.append(ticker)
                print(" ✗ (no data)")

            # Add delay to avoid rate limiting
            time.sleep(0.5)

        except Exception as e:
            failed_tickers.append(ticker)
            print(f" ✗ ({str(e)[:50]})")
            time.sleep(1)

    # Combine all data
    if all_data:
        data = pd.DataFrame(all_data)
    else:
        return pd.DataFrame(), [], {}

    total_days = len(data)
    min_required_days = int(total_days * 0.95)

    valid_tickers = []
    dropped_tickers = {}

    for ticker in data.columns:
        non_null = data[ticker].notna().sum()
        coverage = non_null / total_days

        if non_null < min_required_days:
            dropped_tickers[ticker] = f"Insufficient data: {coverage:.1%} coverage"
        else:
            valid_tickers.append(ticker)

    for ticker in failed_tickers:
        dropped_tickers[ticker] = "Failed to download"

    price_data = data[valid_tickers].copy()
    price_data = price_data.fillna(method='ffill')

    print(f"\n✓ Data Download Complete")
    print(f"  Valid tickers: {len(valid_tickers)}")
    print(f"  Dropped tickers: {len(dropped_tickers)}")
    print(f"  Trading days: {len(price_data):,}")

    if dropped_tickers:
        print(f"\n⚠️  Dropped Tickers:")
        for ticker, reason in dropped_tickers.items():
            print(f"  {ticker}: {reason}")

    return price_data, valid_tickers, dropped_tickers

price_data, valid_tickers, dropped_tickers = download_data(
    tickers=list(PORTFOLIO.keys()),
    start_date=START_DATE,
    end_date=END_DATE
)

# ============================================================================
# PORTFOLIO NORMALIZATION
# ============================================================================

def normalize_portfolio(portfolio_dict, price_data, initial_cash):
    filtered_portfolio = {k: v for k, v in portfolio_dict.items() if k in price_data.columns}
    first_prices = price_data.iloc[0]

    market_values = {}
    for ticker, shares in filtered_portfolio.items():
        market_values[ticker] = shares * first_prices[ticker]

    total_value = sum(market_values.values())
    weights = {ticker: value / total_value for ticker, value in market_values.items()}

    initial_shares = {}
    for ticker, weight in weights.items():
        dollar_allocation = initial_cash * weight
        initial_shares[ticker] = dollar_allocation / first_prices[ticker]

    return weights, initial_shares

weights, initial_shares = normalize_portfolio(
    portfolio_dict=PORTFOLIO,
    price_data=price_data,
    initial_cash=INITIAL_CASH
)

print(f"\n💼 Portfolio normalized: {len(initial_shares)} tickers")

# ============================================================================
# STRATEGY CLASSES
# ============================================================================

class TrimStrategy:
    def __init__(self, price_data, initial_shares, threshold, trim_pct, reinvest_mode):
        self.price_data = price_data
        self.initial_shares = initial_shares
        self.threshold = threshold
        self.trim_pct = trim_pct
        self.reinvest_mode = reinvest_mode
        self.cost_basis = price_data.iloc[0].copy()
        self.holdings = pd.Series(initial_shares)
        self.cash = 0.0
        self.trim_log = []

    def check_and_execute_trims(self, date, prices):
        trim_proceeds = 0.0

        for ticker in self.holdings.index:
            if self.holdings[ticker] == 0:
                continue

            current_price = prices[ticker]
            cost = self.cost_basis[ticker]
            gain = (current_price - cost) / cost

            if gain >= self.threshold:
                shares_to_sell = self.holdings[ticker] * self.trim_pct
                proceeds = shares_to_sell * current_price

                self.holdings[ticker] -= shares_to_sell
                trim_proceeds += proceeds

                self.trim_log.append({
                    'date': date,
                    'ticker': ticker,
                    'gain_pct': gain,
                    'shares_sold': shares_to_sell,
                    'proceeds': proceeds,
                    'price': current_price
                })

        return trim_proceeds

    def reinvest_proceeds(self, proceeds, prices):
        if proceeds == 0:
            return

        if self.reinvest_mode == 'cash':
            self.cash += proceeds
        elif self.reinvest_mode == 'spy':
            if 'SPY' in self.holdings.index:
                spy_shares = proceeds / prices['SPY']
                self.holdings['SPY'] += spy_shares
        elif self.reinvest_mode == 'pro_rata':
            total_value = sum(self.holdings[t] * prices[t] for t in self.holdings.index)

            for ticker in self.holdings.index:
                position_value = self.holdings[ticker] * prices[ticker]
                weight = position_value / total_value if total_value > 0 else 0
                shares_to_buy = (proceeds * weight) / prices[ticker]
                self.holdings[ticker] += shares_to_buy

    def run_backtest(self):
        holdings_history = pd.DataFrame(
            index=self.price_data.index,
            columns=self.price_data.columns,
            data=0.0
        )

        holdings_history.iloc[0] = self.holdings

        for i in range(1, len(self.price_data)):
            date = self.price_data.index[i]
            prices = self.price_data.iloc[i]

            proceeds = self.check_and_execute_trims(date, prices)
            if proceeds > 0:
                self.reinvest_proceeds(proceeds, prices)

            holdings_history.iloc[i] = self.holdings

        return holdings_history

# ============================================================================
# BUY-AND-HOLD BASELINE
# ============================================================================

print("\n" + "="*80)
print("RUNNING BACKTESTS")
print("="*80)

print("\n📈 Running Buy-and-Hold Baseline...")

target_shares = pd.DataFrame(
    data=0.0,
    index=price_data.index,
    columns=price_data.columns
)

for ticker, shares in initial_shares.items():
    target_shares.loc[:, ticker] = shares

bh_portfolio = vbt.Portfolio.from_orders(
    close=price_data,
    size=target_shares,
    size_type='targetamount',
    init_cash=INITIAL_CASH,
    fees=0.001,
    freq='D',
    group_by=True
)

bh_stats = {
    'final_value': bh_portfolio.final_value,
    'total_return': bh_portfolio.total_return,
    'cagr': bh_portfolio.annualized_return,
    'sharpe_ratio': bh_portfolio.sharpe_ratio,
    'sortino_ratio': bh_portfolio.sortino_ratio,
    'max_drawdown': bh_portfolio.max_drawdown,
    'volatility': bh_portfolio.annualized_volatility,
    'num_trades': 0
}

print(f"  ✓ Final Value: ${bh_stats['final_value']:,.2f}")
print(f"  ✓ CAGR: {bh_stats['cagr']:.1%}")
print(f"  ✓ Sharpe Ratio: {bh_stats['sharpe_ratio']:.2f}")

# ============================================================================
# RUN ALL TRIM STRATEGIES
# ============================================================================

all_results = {'Buy-and-Hold': bh_stats}
all_portfolios = {'Buy-and-Hold': bh_portfolio}
all_strategies = {}

for threshold in TRIM_THRESHOLDS:
    for mode in REINVEST_MODES:
        strategy_name = f"Trim@+{int(threshold*100)}% ({mode})"

        print(f"\n🔄 Running: {strategy_name}")

        strategy = TrimStrategy(
            price_data=price_data,
            initial_shares=initial_shares,
            threshold=threshold,
            trim_pct=TRIM_PERCENTAGE,
            reinvest_mode=mode
        )

        holdings_history = strategy.run_backtest()

        portfolio = vbt.Portfolio.from_orders(
            close=price_data,
            size=holdings_history,
            size_type='targetamount',
            init_cash=INITIAL_CASH,
            fees=0.001,
            freq='D',
            group_by=True
        )

        stats = {
            'final_value': portfolio.final_value,
            'total_return': portfolio.total_return,
            'cagr': portfolio.annualized_return,
            'sharpe_ratio': portfolio.sharpe_ratio,
            'sortino_ratio': portfolio.sortino_ratio,
            'max_drawdown': portfolio.max_drawdown,
            'volatility': portfolio.annualized_volatility,
            'num_trades': len(strategy.trim_log),
            'cash_held': strategy.cash
        }

        all_results[strategy_name] = stats
        all_portfolios[strategy_name] = portfolio
        all_strategies[strategy_name] = strategy

        print(f"  Final Value: ${stats['final_value']:,.2f}")
        print(f"  CAGR: {stats['cagr']:.1%}")
        print(f"  Trims: {stats['num_trades']}")

print("\n✓ ALL BACKTESTS COMPLETE")

# ============================================================================
# EXPORT VALIDATOR-COMPATIBLE FILES
# ============================================================================

results_dir = 'results'
os.makedirs(results_dir, exist_ok=True)

print("\n" + "="*80)
print("EXPORTING VALIDATION FILES")
print("="*80)

# Export Buy-and-Hold
print("\n🔄 Exporting Buy-and-Hold...")
strategy_name_clean = "buy_and_hold"

pf_value = bh_portfolio.value()
pf_shares = pd.DataFrame(data=0.0, index=price_data.index, columns=price_data.columns)
for ticker, shares in initial_shares.items():
    pf_shares.loc[:, ticker] = shares

portfolio_value_df = pf_shares.copy()
portfolio_value_df['Cash'] = 0.0
portfolio_value_df['Total_Value'] = pf_value
portfolio_value_df.to_csv(f"{results_dir}/{strategy_name_clean}_portfolio_value.csv")

metrics_df = pd.DataFrame([bh_stats])
metrics_df.to_csv(f"{results_dir}/{strategy_name_clean}_metrics.csv", index=False)

trades_df = pd.DataFrame(columns=['date', 'ticker', 'shares_sold', 'price', 'proceeds', 'gain_pct'])
trades_df.to_csv(f"{results_dir}/{strategy_name_clean}_trades.csv", index=False)

weights_df = pf_shares.copy()
for col in weights_df.columns:
    weights_df[col] = (weights_df[col] * price_data[col]) / portfolio_value_df['Total_Value']
weights_df.to_csv(f"{results_dir}/{strategy_name_clean}_weights.csv")

metadata = {
    'strategy_name': 'Buy-and-Hold',
    'initial_capital': INITIAL_CASH,
    'start_date': START_DATE,
    'end_date': END_DATE,
    'tickers': list(price_data.columns),
    'trim_threshold': None,
    'trim_percentage': None,
    'reinvest_mode': None,
    'fees': 0.001
}
with open(f"{results_dir}/{strategy_name_clean}_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"  ✓ Exported 5 files")

# Export all trim strategies
for threshold in TRIM_THRESHOLDS:
    for mode in REINVEST_MODES:
        strategy_name = f"Trim@+{int(threshold*100)}% ({mode})"
        strategy_name_clean = f"trim_{int(threshold*100)}pct_{mode}"

        print(f"\n🔄 Exporting {strategy_name}...")

        strategy = all_strategies[strategy_name]
        portfolio = all_portfolios[strategy_name]

        # Re-run to get holdings history
        holdings_history = strategy.run_backtest()

        portfolio_value_df = holdings_history.copy()
        portfolio_value_df['Cash'] = strategy.cash
        portfolio_value_df['Total_Value'] = portfolio.value()
        portfolio_value_df.to_csv(f"{results_dir}/{strategy_name_clean}_portfolio_value.csv")

        stats = all_results[strategy_name]
        metrics_df = pd.DataFrame([stats])
        metrics_df.to_csv(f"{results_dir}/{strategy_name_clean}_metrics.csv", index=False)

        trades_df = pd.DataFrame(strategy.trim_log)
        if len(trades_df) > 0:
            trades_df['date'] = pd.to_datetime(trades_df['date'])
        trades_df.to_csv(f"{results_dir}/{strategy_name_clean}_trades.csv", index=False)

        weights_df = holdings_history.copy()
        for col in weights_df.columns:
            weights_df[col] = (weights_df[col] * price_data[col]) / portfolio_value_df['Total_Value']
        weights_df.to_csv(f"{results_dir}/{strategy_name_clean}_weights.csv")

        metadata = {
            'strategy_name': strategy_name,
            'initial_capital': INITIAL_CASH,
            'start_date': START_DATE,
            'end_date': END_DATE,
            'tickers': list(price_data.columns),
            'trim_threshold': threshold,
            'trim_percentage': TRIM_PERCENTAGE,
            'reinvest_mode': mode,
            'fees': 0.001
        }
        with open(f"{results_dir}/{strategy_name_clean}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"  ✓ Exported 5 files ({len(strategy.trim_log)} trades)")

print("\n" + "="*80)
print("✅ ALL FILES EXPORTED")
print("="*80)
print(f"\nFiles saved to: {results_dir}/")
print(f"Total strategies: {len(all_results)}")

# Create comparison summary
comparison_df = pd.DataFrame(all_results).T
comparison_df = comparison_df.sort_values('final_value', ascending=False)
comparison_df.to_csv('trimming_strategy_results.csv')

print("\n📊 Summary Results:")
print(f"  Best strategy: {comparison_df.index[0]}")
print(f"  Best final value: ${comparison_df.iloc[0]['final_value']:,.2f}")
print(f"  Best CAGR: {comparison_df.iloc[0]['cagr']:.2%}")

print("\n✨ Backtest complete! Ready for validation.")
