#!/usr/bin/env python
"""
Portfolio Trimming Strategy Backtest - With 5% Dip-Buy Strategy
Enhanced version that includes "wait for 5% dip before buying SPY/QQQ"
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

print("="*80)
print("PORTFOLIO TRIMMING BACKTEST - WITH 5% DIP-BUY STRATEGY")
print("="*80)

# Configuration
START_DATE = '2015-01-01'
END_DATE = '2025-11-05'
INITIAL_CASH = 100000
TICKERS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']
TRIM_THRESHOLDS = [0.50, 1.00, 1.50]
TRIM_PERCENTAGE = 0.20
REINVEST_MODES = ['pro_rata', 'spy', 'cash', 'dip_buy_5pct']  # NEW!

# Create results directory
results_dir = 'results'
os.makedirs(results_dir, exist_ok=True)

# Generate date range (trading days only)
dates = pd.bdate_range(start=START_DATE, end=END_DATE)
num_days = len(dates)

print(f"\nConfiguration:")
print(f"  Period: {START_DATE} to {END_DATE}")
print(f"  Trading days: {num_days:,}")
print(f"  Tickers: {len(TICKERS)}")
print(f"  Initial capital: ${INITIAL_CASH:,}")
print(f"  NEW: 5% Dip-Buy strategy added!")

# Generate realistic price data (same seed for consistency)
np.random.seed(42)
base_prices = {'AAPL': 25, 'MSFT': 40, 'NVDA': 15, 'TSLA': 50, 'SPY': 200, 'QQQ': 100}
price_growth = {'AAPL': 0.00035, 'MSFT': 0.00040, 'NVDA': 0.00055, 'TSLA': 0.00045, 'SPY': 0.00025, 'QQQ': 0.00030}
volatility = {'AAPL': 0.015, 'MSFT': 0.014, 'NVDA': 0.025, 'TSLA': 0.030, 'SPY': 0.010, 'QQQ': 0.012}

price_data = {}
for ticker in TICKERS:
    prices = [base_prices[ticker]]
    for _ in range(num_days - 1):
        drift = price_growth[ticker]
        shock = np.random.normal(0, volatility[ticker])
        new_price = prices[-1] * (1 + drift + shock)
        prices.append(max(new_price, prices[-1] * 0.95))
    price_data[ticker] = prices

price_df = pd.DataFrame(price_data, index=dates)

print(f"\n✓ Generated price data")

# Calculate initial position sizes (equal weight)
initial_shares = {}
for ticker in TICKERS:
    allocation = INITIAL_CASH / len(TICKERS)
    initial_shares[ticker] = allocation / price_df[ticker].iloc[0]

# ============================================================================
# HELPER FUNCTION: Calculate metrics
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
# GENERATE BUY-AND-HOLD BASELINE (unchanged)
# ============================================================================

print("\n🔄 Generating Buy-and-Hold baseline...")
strategy_name_clean = "buy_and_hold"

portfolio_value_df = pd.DataFrame(index=dates, columns=TICKERS)
for ticker in TICKERS:
    portfolio_value_df[ticker] = initial_shares[ticker]

portfolio_value_df['Cash'] = 0.0
portfolio_value_df['Total_Value'] = sum(portfolio_value_df[ticker] * price_df[ticker] for ticker in TICKERS)

metrics = calculate_metrics(portfolio_value_df['Total_Value'], INITIAL_CASH)
metrics['final_value'] = portfolio_value_df['Total_Value'].iloc[-1]
metrics['num_trades'] = 0
metrics['cash_held'] = 0.0

# Save files (abbreviated for speed)
portfolio_value_df.to_csv(f"{results_dir}/{strategy_name_clean}_portfolio_value.csv")
pd.DataFrame([metrics]).to_csv(f"{results_dir}/{strategy_name_clean}_metrics.csv", index=False)
pd.DataFrame(columns=['date', 'ticker', 'shares_sold', 'price', 'proceeds', 'gain_pct']).to_csv(
    f"{results_dir}/{strategy_name_clean}_trades.csv", index=False
)

metadata = {
    'strategy_name': 'Buy-and-Hold',
    'initial_capital': INITIAL_CASH,
    'start_date': START_DATE,
    'end_date': END_DATE,
    'tickers': TICKERS,
    'fees': 0.001
}
with open(f"{results_dir}/{strategy_name_clean}_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"  ✓ Final Value: ${metrics['final_value']:,.2f}")
print(f"  ✓ CAGR: {metrics['cagr']:.2%}")

# ============================================================================
# GENERATE TRIM STRATEGIES (including new dip-buy)
# ============================================================================

all_results = {'Buy-and-Hold': metrics}

for threshold in TRIM_THRESHOLDS:
    for mode in REINVEST_MODES:
        strategy_name = f"Trim@+{int(threshold*100)}% ({mode.replace('_', '-')})"
        strategy_name_clean = f"trim_{int(threshold*100)}pct_{mode}"

        print(f"\n🔄 Generating {strategy_name}...")

        # Initialize strategy variables
        holdings = {ticker: initial_shares[ticker] for ticker in TICKERS}
        cost_basis = {ticker: price_df[ticker].iloc[0] for ticker in TICKERS}
        cash = 0.0
        trades = []
        holdings_history = []

        # Dip-buy specific variables
        if mode == 'dip_buy_5pct':
            cash_waiting_for_dip = 0.0
            spy_recent_high = price_df['SPY'].iloc[0]
            buy_queue = ['SPY', 'QQQ']
            buy_index = 0
            dip_buys = []  # Track when dips were bought

        for i, date in enumerate(dates):
            day_holdings = holdings.copy()

            # === DIP-BUY LOGIC: Check for 5% drop in SPY ===
            if mode == 'dip_buy_5pct':
                current_spy = price_df['SPY'].iloc[i]

                # Update recent high
                if current_spy > spy_recent_high:
                    spy_recent_high = current_spy

                # Check if 5% dip occurred
                current_drop = (spy_recent_high - current_spy) / spy_recent_high

                if current_drop >= 0.05 and cash_waiting_for_dip > 0:
                    # DIP DETECTED - BUY!
                    next_buy = buy_queue[buy_index]
                    shares_to_buy = cash_waiting_for_dip / price_df[next_buy].iloc[i]
                    holdings[next_buy] += shares_to_buy

                    dip_buys.append({
                        'date': date,
                        'ticker': next_buy,
                        'spy_drop_pct': current_drop,
                        'amount': cash_waiting_for_dip,
                        'shares_bought': shares_to_buy,
                        'price': price_df[next_buy].iloc[i]
                    })

                    cash_waiting_for_dip = 0
                    buy_index = (buy_index + 1) % 2  # Alternate SPY/QQQ
                    spy_recent_high = current_spy  # Reset high

            # === TRIM LOGIC: Check all positions ===
            for ticker in TICKERS:
                if holdings[ticker] > 0:
                    current_price = price_df[ticker].iloc[i]
                    gain = (current_price - cost_basis[ticker]) / cost_basis[ticker]

                    if gain >= threshold:
                        # Execute trim
                        shares_to_sell = holdings[ticker] * TRIM_PERCENTAGE
                        proceeds = shares_to_sell * current_price
                        holdings[ticker] -= shares_to_sell

                        trades.append({
                            'date': date,
                            'ticker': ticker,
                            'shares_sold': shares_to_sell,
                            'price': current_price,
                            'proceeds': proceeds,
                            'gain_pct': gain
                        })

                        # === REINVESTMENT LOGIC ===
                        if mode == 'cash':
                            cash += proceeds
                        elif mode == 'dip_buy_5pct':
                            cash_waiting_for_dip += proceeds
                        elif mode == 'spy':
                            spy_shares = proceeds / price_df['SPY'].iloc[i]
                            holdings['SPY'] += spy_shares
                        elif mode == 'pro_rata':
                            total_value = sum(holdings[t] * price_df[t].iloc[i] for t in TICKERS)
                            for t in TICKERS:
                                weight = (holdings[t] * price_df[t].iloc[i]) / total_value if total_value > 0 else 0
                                shares_to_buy = (proceeds * weight) / price_df[t].iloc[i]
                                holdings[t] += shares_to_buy

                        # Reset trigger
                        cost_basis[ticker] = current_price * 1.05

            holdings_history.append(day_holdings)

        # Create portfolio value DataFrame
        portfolio_value_df = pd.DataFrame(holdings_history, index=dates)

        if mode == 'dip_buy_5pct':
            portfolio_value_df['Cash'] = cash_waiting_for_dip  # Cash waiting for next dip
        else:
            portfolio_value_df['Cash'] = cash

        portfolio_value_df['Total_Value'] = sum(portfolio_value_df[ticker] * price_df[ticker] for ticker in TICKERS)

        # Add cash to total value
        if mode == 'dip_buy_5pct':
            portfolio_value_df['Total_Value'] += cash_waiting_for_dip
        else:
            portfolio_value_df['Total_Value'] += cash

        # Calculate metrics
        metrics = calculate_metrics(portfolio_value_df['Total_Value'], INITIAL_CASH)
        metrics['final_value'] = portfolio_value_df['Total_Value'].iloc[-1]
        metrics['num_trades'] = len(trades)
        metrics['cash_held'] = cash_waiting_for_dip if mode == 'dip_buy_5pct' else cash

        # Extra stats for dip-buy
        if mode == 'dip_buy_5pct':
            metrics['num_dip_buys'] = len(dip_buys)
            metrics['avg_dip_size'] = np.mean([d['spy_drop_pct'] for d in dip_buys]) if dip_buys else 0

        all_results[strategy_name] = metrics

        # Save files
        portfolio_value_df.to_csv(f"{results_dir}/{strategy_name_clean}_portfolio_value.csv")
        pd.DataFrame([metrics]).to_csv(f"{results_dir}/{strategy_name_clean}_metrics.csv", index=False)

        trades_df = pd.DataFrame(trades)
        trades_df.to_csv(f"{results_dir}/{strategy_name_clean}_trades.csv", index=False)

        metadata = {
            'strategy_name': strategy_name,
            'initial_capital': INITIAL_CASH,
            'start_date': START_DATE,
            'end_date': END_DATE,
            'tickers': TICKERS,
            'trim_threshold': threshold,
            'trim_percentage': TRIM_PERCENTAGE,
            'reinvest_mode': mode,
            'fees': 0.001
        }

        if mode == 'dip_buy_5pct':
            metadata['dip_threshold'] = 0.05
            metadata['dip_buys'] = dip_buys  # Include dip buy events

        with open(f"{results_dir}/{strategy_name_clean}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

        # Print results
        print(f"  ✓ Final Value: ${metrics['final_value']:,.2f}")
        print(f"  ✓ CAGR: {metrics['cagr']:.2%}")
        print(f"  ✓ Trims: {len(trades)}")
        if mode == 'dip_buy_5pct':
            print(f"  ✓ Dip Buys: {len(dip_buys)} (avg drop: {metrics['avg_dip_size']:.1%})")
            print(f"  ✓ Cash Waiting: ${cash_waiting_for_dip:,.2f}")

print("\n" + "="*80)
print("✅ BACKTEST COMPLETE")
print("="*80)

# Create comparison summary
comparison_df = pd.DataFrame(all_results).T
comparison_df = comparison_df.sort_values('final_value', ascending=False)

print("\n📊 TOP 5 STRATEGIES:\n")
print(comparison_df.head(5)[['final_value', 'cagr', 'sharpe_ratio', 'max_drawdown']].to_string())

# Highlight dip-buy strategies
dip_strategies = [s for s in comparison_df.index if 'dip-buy' in s]
if dip_strategies:
    print("\n💡 DIP-BUY STRATEGIES PERFORMANCE:\n")
    print(comparison_df.loc[dip_strategies][['final_value', 'cagr', 'num_trades', 'num_dip_buys']].to_string())

comparison_df.to_csv('trimming_strategy_results_with_dip.csv')
print(f"\n✓ Full results saved to: trimming_strategy_results_with_dip.csv")
print("\n🔍 Ready for analysis!")
