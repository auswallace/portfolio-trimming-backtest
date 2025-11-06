#!/usr/bin/env python
"""
Generate realistic mock backtest data for validation demonstration.
This creates validator-compatible files with realistic-looking results.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

print("="*80)
print("GENERATING MOCK BACKTEST DATA FOR VALIDATION DEMONSTRATION")
print("="*80)

# Configuration
START_DATE = '2015-01-01'
END_DATE = '2025-11-05'
INITIAL_CASH = 100000
TICKERS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']
TRIM_THRESHOLDS = [0.50, 1.00, 1.50]
TRIM_PERCENTAGE = 0.20
REINVEST_MODES = ['pro_rata', 'spy', 'cash']

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

# Generate realistic price data
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
        prices.append(max(new_price, prices[-1] * 0.95))  # Prevent extreme drops
    price_data[ticker] = prices

price_df = pd.DataFrame(price_data, index=dates)

print(f"\n✓ Generated price data")
print(f"  Price ranges:")
for ticker in TICKERS:
    print(f"    {ticker}: ${price_df[ticker].iloc[0]:.2f} -> ${price_df[ticker].iloc[-1]:.2f} ({(price_df[ticker].iloc[-1]/price_df[ticker].iloc[0]-1)*100:.1f}%)")

# Calculate initial position sizes (equal weight)
initial_shares = {}
for ticker in TICKERS:
    allocation = INITIAL_CASH / len(TICKERS)
    initial_shares[ticker] = allocation / price_df[ticker].iloc[0]

# ============================================================================
# GENERATE BUY-AND-HOLD BASELINE
# ============================================================================

print("\n🔄 Generating Buy-and-Hold baseline...")
strategy_name_clean = "buy_and_hold"

# Portfolio value
portfolio_value_df = pd.DataFrame(index=dates, columns=TICKERS)
for ticker in TICKERS:
    portfolio_value_df[ticker] = initial_shares[ticker]

portfolio_value_df['Cash'] = 0.0
portfolio_value_df['Total_Value'] = sum(portfolio_value_df[ticker] * price_df[ticker] for ticker in TICKERS)
portfolio_value_df.to_csv(f"{results_dir}/{strategy_name_clean}_portfolio_value.csv")

# Metrics
total_return = (portfolio_value_df['Total_Value'].iloc[-1] / INITIAL_CASH) - 1
years = (datetime.strptime(END_DATE, '%Y-%m-%d') - datetime.strptime(START_DATE, '%Y-%m-%d')).days / 365.25
cagr = (1 + total_return) ** (1 / years) - 1

returns = portfolio_value_df['Total_Value'].pct_change().dropna()
sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
downside_returns = returns[returns < 0]
sortino = (returns.mean() * 252) / (downside_returns.std() * np.sqrt(252))

running_max = portfolio_value_df['Total_Value'].cummax()
drawdown = (portfolio_value_df['Total_Value'] - running_max) / running_max
max_drawdown = drawdown.min()
volatility_annual = returns.std() * np.sqrt(252)

metrics = {
    'final_value': portfolio_value_df['Total_Value'].iloc[-1],
    'total_return': total_return,
    'cagr': cagr,
    'sharpe_ratio': sharpe,
    'sortino_ratio': sortino,
    'max_drawdown': max_drawdown,
    'volatility': volatility_annual,
    'num_trades': 0,
    'cash_held': 0.0
}
pd.DataFrame([metrics]).to_csv(f"{results_dir}/{strategy_name_clean}_metrics.csv", index=False)

# Trades (empty)
pd.DataFrame(columns=['date', 'ticker', 'shares_sold', 'price', 'proceeds', 'gain_pct']).to_csv(
    f"{results_dir}/{strategy_name_clean}_trades.csv", index=False
)

# Weights
weights_df = pd.DataFrame(index=dates, columns=TICKERS)
for ticker in TICKERS:
    weights_df[ticker] = (portfolio_value_df[ticker] * price_df[ticker]) / portfolio_value_df['Total_Value']
weights_df.to_csv(f"{results_dir}/{strategy_name_clean}_weights.csv")

# Metadata
metadata = {
    'strategy_name': 'Buy-and-Hold',
    'initial_capital': INITIAL_CASH,
    'start_date': START_DATE,
    'end_date': END_DATE,
    'tickers': TICKERS,
    'trim_threshold': None,
    'trim_percentage': None,
    'reinvest_mode': None,
    'fees': 0.001
}
with open(f"{results_dir}/{strategy_name_clean}_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"  ✓ Final Value: ${metrics['final_value']:,.2f}")
print(f"  ✓ CAGR: {metrics['cagr']:.2%}")
print(f"  ✓ Sharpe: {metrics['sharpe_ratio']:.2f}")

# ============================================================================
# GENERATE TRIM STRATEGIES
# ============================================================================

for threshold in TRIM_THRESHOLDS:
    for mode in REINVEST_MODES:
        strategy_name = f"Trim@+{int(threshold*100)}% ({mode})"
        strategy_name_clean = f"trim_{int(threshold*100)}pct_{mode}"

        print(f"\n🔄 Generating {strategy_name}...")

        # Simulate trim strategy
        holdings = {ticker: initial_shares[ticker] for ticker in TICKERS}
        cost_basis = {ticker: price_df[ticker].iloc[0] for ticker in TICKERS}
        cash = 0.0
        trades = []
        holdings_history = []

        for i, date in enumerate(dates):
            day_holdings = holdings.copy()

            # Check for trim triggers
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

                        # Reinvest
                        if mode == 'cash':
                            cash += proceeds
                        elif mode == 'spy':
                            spy_shares = proceeds / price_df['SPY'].iloc[i]
                            holdings['SPY'] += spy_shares
                        elif mode == 'pro_rata':
                            total_value = sum(holdings[t] * price_df[t].iloc[i] for t in TICKERS)
                            for t in TICKERS:
                                weight = (holdings[t] * price_df[t].iloc[i]) / total_value if total_value > 0 else 0
                                shares_to_buy = (proceeds * weight) / price_df[t].iloc[i]
                                holdings[t] += shares_to_buy

                        # Reset trigger (in reality would track last trim, but simplified here)
                        cost_basis[ticker] = current_price * 1.05  # Raise threshold slightly

            holdings_history.append(day_holdings)

        # Create portfolio value DataFrame
        portfolio_value_df = pd.DataFrame(holdings_history, index=dates)
        portfolio_value_df['Cash'] = cash
        portfolio_value_df['Total_Value'] = sum(portfolio_value_df[ticker] * price_df[ticker] for ticker in TICKERS) + cash
        portfolio_value_df.to_csv(f"{results_dir}/{strategy_name_clean}_portfolio_value.csv")

        # Metrics
        total_return = (portfolio_value_df['Total_Value'].iloc[-1] / INITIAL_CASH) - 1
        cagr = (1 + total_return) ** (1 / years) - 1

        returns = portfolio_value_df['Total_Value'].pct_change().dropna()
        sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
        downside_returns = returns[returns < 0]
        sortino = (returns.mean() * 252) / (downside_returns.std() * np.sqrt(252)) if len(downside_returns) > 0 else 0

        running_max = portfolio_value_df['Total_Value'].cummax()
        drawdown = (portfolio_value_df['Total_Value'] - running_max) / running_max
        max_drawdown = drawdown.min()
        volatility_annual = returns.std() * np.sqrt(252)

        metrics = {
            'final_value': portfolio_value_df['Total_Value'].iloc[-1],
            'total_return': total_return,
            'cagr': cagr,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_drawdown,
            'volatility': volatility_annual,
            'num_trades': len(trades),
            'cash_held': cash
        }
        pd.DataFrame([metrics]).to_csv(f"{results_dir}/{strategy_name_clean}_metrics.csv", index=False)

        # Trades
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv(f"{results_dir}/{strategy_name_clean}_trades.csv", index=False)

        # Weights
        weights_df = pd.DataFrame(index=dates, columns=TICKERS)
        for ticker in TICKERS:
            weights_df[ticker] = (portfolio_value_df[ticker] * price_df[ticker]) / portfolio_value_df['Total_Value']
        weights_df.to_csv(f"{results_dir}/{strategy_name_clean}_weights.csv")

        # Metadata
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
        with open(f"{results_dir}/{strategy_name_clean}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"  ✓ Final Value: ${metrics['final_value']:,.2f}")
        print(f"  ✓ CAGR: {metrics['cagr']:.2%}")
        print(f"  ✓ Trims: {len(trades)}")

print("\n" + "="*80)
print("✅ MOCK DATA GENERATION COMPLETE")
print("="*80)
print(f"\nGenerated files in: {results_dir}/")
print(f"Total strategies: 10 (1 baseline + 9 trim variations)")
print("\n🔍 Ready for validation!")
