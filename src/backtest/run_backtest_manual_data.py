#!/usr/bin/env python
"""
Portfolio Trimming Backtest - Using Manually Downloaded CSV Data
Reads Yahoo Finance CSVs from manual_data/ folder
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import glob

print("="*80)
print("PORTFOLIO TRIMMING BACKTEST - REAL DATA FROM MANUAL CSV FILES")
print("="*80)

# Configuration
START_DATE = '2015-01-01'
END_DATE = '2024-11-05'
INITIAL_CASH = 100000
TICKERS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']
TRIM_THRESHOLDS = [0.50, 1.00, 1.50]
TRIM_PERCENTAGE = 0.20
REINVEST_MODES = ['pro_rata', 'spy', 'cash', 'dip_buy_5pct']

# Directory for manual CSV files
MANUAL_DATA_DIR = 'manual_data'

print(f"\n📁 Looking for CSV files in: {MANUAL_DATA_DIR}/")

# ============================================================================
# STEP 1: Load Manual CSV Files
# ============================================================================

def load_manual_csv_data(data_dir, tickers, start_date, end_date):
    """Load historical price data from manually downloaded Yahoo Finance CSVs"""

    print(f"\n📊 Loading manual CSV files...")

    if not os.path.exists(data_dir):
        print(f"\n❌ ERROR: Directory '{data_dir}/' not found!")
        print(f"\nPlease create it and add CSV files:")
        print(f"  mkdir {data_dir}")
        print(f"  # Then download CSVs from Yahoo Finance")
        print(f"\nSee MANUAL_DATA_INSTRUCTIONS.md for details")
        return None, []

    all_data = {}
    failed_tickers = []

    for ticker in tickers:
        csv_file = f"{data_dir}/{ticker}.csv"

        print(f"  Loading {ticker}...", end='')

        if not os.path.exists(csv_file):
            print(f" ✗ (file not found: {csv_file})")
            failed_tickers.append(ticker)
            continue

        try:
            # Read Yahoo Finance CSV format
            df = pd.read_csv(csv_file)

            # Parse date column with UTC and immediately convert to timezone-naive
            df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
            df.set_index('Date', inplace=True)

            # Yahoo CSVs have 'Close' column
            if 'Close' in df.columns:
                ticker_data = df['Close']
            else:
                print(f" ✗ (no price column found)")
                failed_tickers.append(ticker)
                continue

            # Filter date range
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            ticker_data = ticker_data[(ticker_data.index >= start_dt) & (ticker_data.index <= end_dt)]

            if len(ticker_data) > 0:
                all_data[ticker] = ticker_data
                print(f" ✓ ({len(ticker_data)} days)")
            else:
                print(f" ✗ (no data in date range)")
                failed_tickers.append(ticker)

        except Exception as e:
            print(f" ✗ ({str(e)[:50]})")
            failed_tickers.append(ticker)

    if not all_data:
        print(f"\n❌ No data loaded! Check that CSV files exist in {data_dir}/")
        return None, []

    # Combine into single DataFrame
    price_df = pd.DataFrame(all_data)

    # Forward fill missing data (holidays)
    price_df = price_df.fillna(method='ffill')

    # Drop any remaining NaN rows
    price_df = price_df.dropna()

    valid_tickers = list(price_df.columns)

    print(f"\n✓ Data Loading Complete")
    print(f"  Valid tickers: {len(valid_tickers)}")
    print(f"  Failed tickers: {len(failed_tickers)}")
    print(f"  Trading days: {len(price_df):,}")
    print(f"  Date range: {price_df.index[0].date()} to {price_df.index[-1].date()}")

    if failed_tickers:
        print(f"\n⚠️  Failed to load: {', '.join(failed_tickers)}")

    # Show price ranges
    print(f"\n📈 Price Ranges:")
    for ticker in valid_tickers:
        start_price = price_df[ticker].iloc[0]
        end_price = price_df[ticker].iloc[-1]
        total_return = (end_price / start_price - 1) * 100
        print(f"  {ticker}: ${start_price:.2f} → ${end_price:.2f} ({total_return:+.1f}%)")

    return price_df, valid_tickers

# Load the data
price_data = load_manual_csv_data(MANUAL_DATA_DIR, TICKERS, START_DATE, END_DATE)

if price_data[0] is None:
    print("\n❌ Cannot proceed without data!")
    print("\n📋 Next Steps:")
    print("1. Create manual_data/ folder: mkdir manual_data")
    print("2. Download CSVs from Yahoo Finance (see MANUAL_DATA_INSTRUCTIONS.md)")
    print("3. Move CSV files to manual_data/ folder")
    print("4. Run this script again")
    exit(1)

price_df, valid_tickers = price_data

# Create results directory
results_dir = 'results_real_data'
os.makedirs(results_dir, exist_ok=True)
print(f"\n📁 Results will be saved to: {results_dir}/")

dates = price_df.index
num_days = len(dates)

# Calculate initial position sizes (equal weight)
initial_shares = {}
for ticker in valid_tickers:
    allocation = INITIAL_CASH / len(valid_tickers)
    initial_shares[ticker] = allocation / price_df[ticker].iloc[0]

# ============================================================================
# HELPER FUNCTIONS (same as before)
# ============================================================================

def calculate_metrics(portfolio_value_series, initial_capital):
    """Calculate all performance metrics from portfolio value series"""
    total_return = (portfolio_value_series.iloc[-1] / initial_capital) - 1
    years = len(portfolio_value_series) / 252
    cagr = (1 + total_return) ** (1 / years) - 1

    returns = portfolio_value_series.pct_change().dropna()
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0

    downside_returns = returns[returns < 0]
    sortino = (returns.mean() * 252) / (downside_returns.std() * np.sqrt(252)) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0

    running_max = portfolio_value_series.cummax()
    drawdown = (portfolio_value_series - running_max) / running_max
    max_drawdown = drawdown.min()
    volatility_annual = returns.std() * np.sqrt(252)

    return {
        'total_return': total_return,
        'cagr': cagr,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown': max_drawdown,
        'volatility': volatility_annual
    }

# ============================================================================
# RUN ALL STRATEGIES (same logic as mock data version)
# ============================================================================

print("\n" + "="*80)
print("RUNNING BACKTESTS WITH REAL DATA")
print("="*80)

all_results = {}

# Buy-and-Hold
print("\n🔄 Running Buy-and-Hold baseline...")
portfolio_value_df = pd.DataFrame(index=dates, columns=valid_tickers)
for ticker in valid_tickers:
    portfolio_value_df[ticker] = initial_shares[ticker]

portfolio_value_df['Cash'] = 0.0
portfolio_value_df['Total_Value'] = sum(portfolio_value_df[ticker] * price_df[ticker] for ticker in valid_tickers)

metrics = calculate_metrics(portfolio_value_df['Total_Value'], INITIAL_CASH)
metrics['final_value'] = portfolio_value_df['Total_Value'].iloc[-1]
metrics['num_trades'] = 0
metrics['cash_held'] = 0.0

all_results['Buy-and-Hold'] = metrics

print(f"  ✓ Final Value: ${metrics['final_value']:,.2f}")
print(f"  ✓ CAGR: {metrics['cagr']:.2%}")
print(f"  ✓ Sharpe: {metrics['sharpe_ratio']:.2f}")

# Trim strategies (abbreviated - same logic as run_backtest_with_dip.py)
for threshold in TRIM_THRESHOLDS:
    for mode in REINVEST_MODES:
        strategy_name = f"Trim@+{int(threshold*100)}% ({mode.replace('_', '-')})"

        print(f"\n🔄 Running: {strategy_name}...")

        holdings = {ticker: initial_shares[ticker] for ticker in valid_tickers}
        cost_basis = {ticker: price_df[ticker].iloc[0] for ticker in valid_tickers}
        cash = 0.0
        trades = []

        if mode == 'dip_buy_5pct':
            cash_waiting_for_dip = 0.0
            spy_recent_high = price_df['SPY'].iloc[0] if 'SPY' in valid_tickers else 0
            buy_queue = ['SPY', 'QQQ']
            buy_index = 0
            dip_buys = []

        holdings_history = []

        for i, date in enumerate(dates):
            # Dip-buy logic
            if mode == 'dip_buy_5pct' and 'SPY' in valid_tickers:
                current_spy = price_df['SPY'].iloc[i]
                if current_spy > spy_recent_high:
                    spy_recent_high = current_spy

                current_drop = (spy_recent_high - current_spy) / spy_recent_high

                if current_drop >= 0.05 and cash_waiting_for_dip > 0:
                    next_buy = buy_queue[buy_index]
                    if next_buy in valid_tickers:
                        shares_to_buy = cash_waiting_for_dip / price_df[next_buy].iloc[i]
                        holdings[next_buy] += shares_to_buy

                        dip_buys.append({
                            'date': date,
                            'ticker': next_buy,
                            'spy_drop_pct': current_drop,
                            'amount': cash_waiting_for_dip,
                            'price': price_df[next_buy].iloc[i]
                        })

                        cash_waiting_for_dip = 0
                        buy_index = (buy_index + 1) % 2
                        spy_recent_high = current_spy

            # Trim logic
            for ticker in valid_tickers:
                if holdings[ticker] > 0:
                    current_price = price_df[ticker].iloc[i]
                    gain = (current_price - cost_basis[ticker]) / cost_basis[ticker]

                    if gain >= threshold:
                        shares_to_sell = holdings[ticker] * TRIM_PERCENTAGE
                        proceeds = shares_to_sell * current_price
                        holdings[ticker] -= shares_to_sell

                        trades.append({
                            'date': date,
                            'ticker': ticker,
                            'proceeds': proceeds,
                            'gain_pct': gain
                        })

                        if mode == 'cash':
                            cash += proceeds
                        elif mode == 'dip_buy_5pct':
                            cash_waiting_for_dip += proceeds
                        elif mode == 'spy' and 'SPY' in valid_tickers:
                            holdings['SPY'] += proceeds / price_df['SPY'].iloc[i]
                        elif mode == 'pro_rata':
                            total_value = sum(holdings[t] * price_df[t].iloc[i] for t in valid_tickers)
                            for t in valid_tickers:
                                weight = (holdings[t] * price_df[t].iloc[i]) / total_value if total_value > 0 else 0
                                holdings[t] += (proceeds * weight) / price_df[t].iloc[i]

                        cost_basis[ticker] = current_price * 1.05

            holdings_history.append(holdings.copy())

        # Calculate portfolio value
        portfolio_value_df = pd.DataFrame(holdings_history, index=dates)
        portfolio_value_df['Cash'] = cash_waiting_for_dip if mode == 'dip_buy_5pct' else cash
        portfolio_value_df['Total_Value'] = sum(portfolio_value_df[ticker] * price_df[ticker] for ticker in valid_tickers) + portfolio_value_df['Cash']

        metrics = calculate_metrics(portfolio_value_df['Total_Value'], INITIAL_CASH)
        metrics['final_value'] = portfolio_value_df['Total_Value'].iloc[-1]
        metrics['num_trades'] = len(trades)
        metrics['cash_held'] = cash_waiting_for_dip if mode == 'dip_buy_5pct' else cash

        if mode == 'dip_buy_5pct':
            metrics['num_dip_buys'] = len(dip_buys)
            metrics['avg_dip_size'] = np.mean([d['spy_drop_pct'] for d in dip_buys]) if dip_buys else 0

        all_results[strategy_name] = metrics

        print(f"  ✓ Final Value: ${metrics['final_value']:,.2f}")
        print(f"  ✓ CAGR: {metrics['cagr']:.2%}")
        print(f"  ✓ Trims: {len(trades)}")
        if mode == 'dip_buy_5pct':
            print(f"  ✓ Dip Buys: {len(dip_buys)}")

print("\n" + "="*80)
print("✅ REAL DATA BACKTEST COMPLETE")
print("="*80)

# Create comparison
comparison_df = pd.DataFrame(all_results).T
comparison_df = comparison_df.sort_values('final_value', ascending=False)

print("\n🏆 TOP 5 STRATEGIES (REAL DATA):\n")
print(comparison_df.head(5)[['final_value', 'cagr', 'sharpe_ratio', 'max_drawdown']].to_string())

dip_strategies = [s for s in comparison_df.index if 'dip-buy' in s]
if dip_strategies:
    print("\n💡 DIP-BUY STRATEGIES (REAL DATA):\n")
    print(comparison_df.loc[dip_strategies][['final_value', 'cagr', 'num_trades', 'num_dip_buys']].to_string())

comparison_df.to_csv(f'{results_dir}/real_data_results.csv')

print(f"\n✓ Results saved to: {results_dir}/real_data_results.csv")
print("\n✨ Ready to compare with mock data results!")
