#!/usr/bin/env python
"""
Portfolio Trimming Backtest - INDEX-FOCUSED REALISTIC SCENARIO

Tests trimming strategy on a REALISTIC portfolio:
- Primarily index funds (SPY, QQQ, VOO)
- A few large-cap stocks you might actually have bought in 2015
- NO NVDA at $0.48 (unrealistic)

This represents a typical investor's portfolio, not perfect stock-picking.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

print("="*80)
print("PORTFOLIO TRIMMING BACKTEST - REALISTIC INDEX-FOCUSED PORTFOLIO")
print("="*80)

# Configuration
START_DATE = '2015-01-01'
END_DATE = '2024-11-05'
INITIAL_CASH = 100000
TRIM_PERCENTAGE = 0.20

# COST & TAX TOGGLES (set to 0 to disable)
TRANSACTION_COST_PCT = 0.0     # 0.001 = 0.1% per trade (both buys and sells)
CAPITAL_GAINS_TAX_RATE = 0.0   # 0.20 = 20% long-term capital gains tax

# TRIMMING STRATEGIES
TRIM_THRESHOLDS = [0.50, 1.00, 1.50]  # Threshold-based: +50%, +100%, +150%
MOMENTUM_THRESHOLD = 1.30  # Momentum-guided: price > 1.3x 200-day MA
MOMENTUM_LOOKBACK = 20     # and 20-day momentum < 0
VOLATILITY_THRESHOLDS = [1.5, 2.0, 2.5]  # Test multiple thresholds
VOLATILITY_COOLDOWN_DAYS = 10  # Minimum days between trims per ticker
VOLATILITY_HYSTERESIS = 0.9  # Exit threshold = entry * hysteresis (e.g., 1.5 entry, 1.35 exit)

# REINVESTMENT MODELS
REINVEST_MODES = ['pro_rata', 'spy', 'cash', 'dip_buy_5pct', 'drip', 'yield_volatility']

# Strategy types
TRIM_STRATEGIES = ['threshold', 'momentum', 'volatility']

# REALISTIC PORTFOLIO (what you might have actually bought in 2015)
# 60% index funds, 40% large-cap stocks
PORTFOLIO_CONFIG = {
    'SPY': 0.30,   # 30% S&P 500
    'QQQ': 0.20,   # 20% Nasdaq
    'VOO': 0.10,   # 10% Vanguard S&P (similar to SPY)
    'AAPL': 0.15,  # 15% Apple (realistic to have bought)
    'MSFT': 0.15,  # 15% Microsoft (realistic)
    'TSLA': 0.10,  # 10% Tesla (IF you were early adopter)
}

TICKERS = list(PORTFOLIO_CONFIG.keys())

print(f"\n📊 Realistic Portfolio Allocation:")
for ticker, weight in PORTFOLIO_CONFIG.items():
    print(f"  {ticker}: {weight*100:.0f}%")

print(f"\nThis represents a typical investor who:")
print(f"  ✓ Invests mostly in index funds (60%)")
print(f"  ✓ Adds some blue-chip stocks (30%)")
print(f"  ✓ Maybe got lucky with Tesla (10%)")
print(f"  ✗ Did NOT buy NVDA at $0.48 (that's lottery-level luck)")

print(f"\n💰 Cost & Tax Settings:")
if TRANSACTION_COST_PCT > 0:
    print(f"  ✓ Transaction costs: {TRANSACTION_COST_PCT*100:.2f}% per trade")
else:
    print(f"  ✗ Transaction costs: DISABLED")
if CAPITAL_GAINS_TAX_RATE > 0:
    print(f"  ✓ Capital gains tax: {CAPITAL_GAINS_TAX_RATE*100:.1f}%")
else:
    print(f"  ✗ Capital gains tax: DISABLED")

# Directory for manual CSV files
MANUAL_DATA_DIR = 'data'

# ============================================================================
# LOAD DATA
# ============================================================================

def load_manual_csv_data(data_dir, tickers, start_date, end_date):
    """Load historical price data from manually downloaded Yahoo Finance CSVs"""

    print(f"\n📂 Loading CSV files from: {data_dir}/")

    if not os.path.exists(data_dir):
        print(f"\n❌ ERROR: Directory '{data_dir}/' not found!")
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
    price_df = price_df.ffill()

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
    print("\n📋 Need to download VOO.csv:")
    print("Run: python download_with_cache.py")
    print("(Edit TICKERS list to include VOO)")
    exit(1)

price_df, valid_tickers = price_data

# Create results directory
results_dir = 'results_index_focus'
os.makedirs(results_dir, exist_ok=True)
print(f"\n📁 Results will be saved to: {results_dir}/")

dates = price_df.index
num_days = len(dates)

# Calculate initial position sizes based on PORTFOLIO_CONFIG
initial_shares = {}
for ticker in valid_tickers:
    if ticker in PORTFOLIO_CONFIG:
        allocation = INITIAL_CASH * PORTFOLIO_CONFIG[ticker]
        initial_shares[ticker] = allocation / price_df[ticker].iloc[0]
    else:
        # Equal weight for any unexpected tickers
        allocation = INITIAL_CASH / len(valid_tickers)
        initial_shares[ticker] = allocation / price_df[ticker].iloc[0]

print(f"\n💼 Initial Position Sizes:")
for ticker in valid_tickers:
    value = initial_shares[ticker] * price_df[ticker].iloc[0]
    print(f"  {ticker}: {initial_shares[ticker]:.2f} shares (${value:,.2f})")

# ============================================================================
# CALCULATE TECHNICAL INDICATORS
# ============================================================================

print("\n📊 Calculating technical indicators...")

# Calculate 200-day moving average for all tickers
ma_200 = price_df.rolling(window=200).mean()

# Calculate 20-day momentum (percentage change over 20 days)
momentum_20 = price_df.pct_change(periods=20)

# Calculate 30-day realized volatility
returns_df = price_df.pct_change()
volatility_30 = returns_df.rolling(window=30).std() * np.sqrt(252)  # Annualized

# Calculate 1-year (252 days) median volatility
volatility_252_median = returns_df.rolling(window=252).std().rolling(window=252).median() * np.sqrt(252)

print("  ✓ 200-day moving averages")
print("  ✓ 20-day momentum")
print("  ✓ 30-day realized volatility")
print("  ✓ 1-year median volatility")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_rolling_metrics(portfolio_value_series, window_days=756):
    """
    Calculate rolling 3-year metrics

    Args:
        portfolio_value_series: Portfolio value time series
        window_days: Rolling window size (756 days = 3 years * 252 trading days)

    Returns:
        dict with rolling_cagr and rolling_max_dd series
    """
    rolling_cagr = []
    rolling_max_dd = []

    for i in range(window_days, len(portfolio_value_series)):
        window = portfolio_value_series.iloc[i-window_days:i+1]

        # Calculate 3-year CAGR
        start_val = window.iloc[0]
        end_val = window.iloc[-1]
        years = window_days / 252
        cagr = (end_val / start_val) ** (1 / years) - 1
        rolling_cagr.append(cagr)

        # Calculate max drawdown in window
        running_max = window.cummax()
        drawdown = (window - running_max) / running_max
        max_dd = drawdown.min()
        rolling_max_dd.append(max_dd)

    return {
        'rolling_3yr_cagr': pd.Series(rolling_cagr, index=portfolio_value_series.index[window_days:]),
        'rolling_3yr_max_dd': pd.Series(rolling_max_dd, index=portfolio_value_series.index[window_days:])
    }

def calculate_bootstrap_ci(portfolio_value_series, initial_capital, n_bootstrap=1000, confidence=0.95):
    """
    Calculate bootstrapped confidence intervals for CAGR and Sharpe

    Args:
        portfolio_value_series: Portfolio value time series
        initial_capital: Initial investment
        n_bootstrap: Number of bootstrap iterations
        confidence: Confidence level (default 0.95 for 95% CI)

    Returns:
        dict with CI bounds for CAGR and Sharpe
    """
    returns = portfolio_value_series.pct_change().dropna()
    returns_capped = returns.clip(-0.5, 0.5)  # Cap extreme returns
    n_days = len(returns_capped)
    years = n_days / 252

    bootstrap_cagrs = []
    bootstrap_sharpes = []

    for _ in range(n_bootstrap):
        # Resample with replacement
        sample_returns = returns_capped.sample(n=n_days, replace=True)

        # Calculate CAGR for this sample
        cumulative_return = (1 + sample_returns).prod() - 1
        sample_cagr = (1 + cumulative_return) ** (1 / years) - 1
        bootstrap_cagrs.append(sample_cagr)

        # Calculate Sharpe for this sample
        sample_sharpe = (sample_returns.mean() * 252) / (sample_returns.std() * np.sqrt(252)) if sample_returns.std() > 0 else 0
        bootstrap_sharpes.append(sample_sharpe)

    # Calculate confidence intervals
    alpha = (1 - confidence) / 2
    lower_percentile = alpha * 100
    upper_percentile = (1 - alpha) * 100

    return {
        'cagr_ci_lower': np.percentile(bootstrap_cagrs, lower_percentile),
        'cagr_ci_upper': np.percentile(bootstrap_cagrs, upper_percentile),
        'sharpe_ci_lower': np.percentile(bootstrap_sharpes, lower_percentile),
        'sharpe_ci_upper': np.percentile(bootstrap_sharpes, upper_percentile)
    }

def calculate_metrics(portfolio_value_series, initial_capital):
    """Calculate all performance metrics from portfolio value series"""

    # Validate input
    if len(portfolio_value_series) == 0:
        return {'total_return': 0, 'cagr': 0, 'sharpe_ratio': 0, 'sortino_ratio': 0, 'max_drawdown': 0, 'volatility': 0}

    # Check for NaN or Inf values
    if portfolio_value_series.isna().any() or np.isinf(portfolio_value_series).any():
        print("    ⚠️  WARNING: Portfolio contains NaN or Inf values!")
        portfolio_value_series = portfolio_value_series.replace([np.inf, -np.inf], np.nan).ffill()

    total_return = (portfolio_value_series.iloc[-1] / initial_capital) - 1
    years = len(portfolio_value_series) / 252
    cagr = (1 + total_return) ** (1 / years) - 1

    returns = portfolio_value_series.pct_change().dropna()

    # Detect extreme returns (likely bugs)
    extreme_returns = returns[abs(returns) > 0.5]  # >50% daily moves
    if len(extreme_returns) > 0:
        print(f"    ⚠️  WARNING: {len(extreme_returns)} extreme daily returns detected (>50%)")
        print(f"       Max: {returns.max():.2%}, Min: {returns.min():.2%}")

    # Cap extreme returns to prevent metric distortion
    returns_capped = returns.clip(-0.5, 0.5)

    sharpe = (returns_capped.mean() * 252) / (returns_capped.std() * np.sqrt(252)) if returns_capped.std() > 0 else 0

    downside_returns = returns_capped[returns_capped < 0]
    sortino = (returns_capped.mean() * 252) / (downside_returns.std() * np.sqrt(252)) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0

    running_max = portfolio_value_series.cummax()
    drawdown = (portfolio_value_series - running_max) / running_max
    max_drawdown = drawdown.min()
    volatility_annual = returns_capped.std() * np.sqrt(252)

    # Calculate rolling 3-year metrics
    rolling_metrics = calculate_rolling_metrics(portfolio_value_series)

    # Calculate bootstrap confidence intervals
    bootstrap_ci = calculate_bootstrap_ci(portfolio_value_series, initial_capital)

    return {
        'total_return': total_return,
        'cagr': cagr,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown': max_drawdown,
        'volatility': volatility_annual,
        'rolling_3yr_cagr_mean': rolling_metrics['rolling_3yr_cagr'].mean(),
        'rolling_3yr_cagr_std': rolling_metrics['rolling_3yr_cagr'].std(),
        'rolling_3yr_max_dd_mean': rolling_metrics['rolling_3yr_max_dd'].mean(),
        'rolling_3yr_max_dd_worst': rolling_metrics['rolling_3yr_max_dd'].min(),
        **bootstrap_ci
    }

def should_trim_threshold(current_price, cost_basis, threshold):
    """Check if position should be trimmed based on threshold strategy"""
    gain = (current_price - cost_basis) / cost_basis
    return gain >= threshold

def should_trim_momentum(ticker, i, price_df, ma_200, momentum_20):
    """Check if position should be trimmed based on momentum strategy"""
    if i < 200:  # Need 200 days for MA
        return False

    current_price = price_df[ticker].iloc[i]
    ma_200_value = ma_200[ticker].iloc[i]
    momentum_value = momentum_20[ticker].iloc[i]

    # Trim when price > 1.3x 200-day MA AND 20-day momentum < 0
    if pd.notna(ma_200_value) and pd.notna(momentum_value):
        return (current_price / ma_200_value > MOMENTUM_THRESHOLD) and (momentum_value < 0)
    return False

def should_trim_volatility(ticker, i, volatility_30, volatility_252_median, vol_threshold,
                           last_trim_dates, current_date, trim_active):
    """
    Check if position should be trimmed based on volatility strategy

    Args:
        ticker: ticker symbol
        i: current date index
        volatility_30: 30-day volatility series
        volatility_252_median: 1-year median volatility series
        vol_threshold: volatility threshold multiplier (e.g., 1.5, 2.0, 2.5)
        last_trim_dates: dict tracking last trim date per ticker
        current_date: current date
        trim_active: dict tracking if trim condition is currently active per ticker

    Returns:
        bool: True if should trim
    """
    if i < 252:  # Need 252 days for median volatility
        return False

    vol_30_value = volatility_30[ticker].iloc[i]
    vol_median_value = volatility_252_median[ticker].iloc[i]

    if not (pd.notna(vol_30_value) and pd.notna(vol_median_value) and vol_median_value > 0):
        return False

    # Calculate current ratio
    vol_ratio = vol_30_value / vol_median_value

    # HYSTERESIS: Use different thresholds for entry vs exit
    entry_threshold = vol_threshold
    exit_threshold = vol_threshold * VOLATILITY_HYSTERESIS  # e.g., 1.5 * 0.9 = 1.35

    # Update trim_active state with hysteresis
    if ticker not in trim_active:
        trim_active[ticker] = False

    if not trim_active[ticker] and vol_ratio > entry_threshold:
        trim_active[ticker] = True
    elif trim_active[ticker] and vol_ratio < exit_threshold:
        trim_active[ticker] = False

    # Only trim if condition is active
    if not trim_active[ticker]:
        return False

    # COOLDOWN: Check if enough time has passed since last trim
    if ticker in last_trim_dates:
        days_since_trim = (current_date - last_trim_dates[ticker]).days
        if days_since_trim < VOLATILITY_COOLDOWN_DAYS:
            return False

    return True

def run_single_strategy(strategy_type, threshold, reinvest_mode,
                        price_df, dates, valid_tickers, initial_shares,
                        ma_200, momentum_20, volatility_30, volatility_252_median):
    """
    Run a single backtest strategy

    Args:
        strategy_type: 'threshold', 'momentum', or 'volatility'
        threshold: gain threshold for threshold-based strategies (ignored for others)
        reinvest_mode: 'pro_rata', 'spy', 'cash', 'dip_buy_5pct', 'drip', 'yield_volatility'
        ... (data structures)

    Returns:
        dict: metrics including final_value, cagr, sharpe_ratio, etc.
    """
    holdings = {ticker: initial_shares[ticker] for ticker in valid_tickers}
    cost_basis = {ticker: price_df[ticker].iloc[0] for ticker in valid_tickers}
    cash = 0.0
    trades = []

    # Volatility strategy state tracking
    last_trim_dates = {}  # Track last trim date per ticker for cooldown
    trim_active = {}  # Track if trim condition is active per ticker for hysteresis

    # Mode-specific initialization
    if reinvest_mode == 'dip_buy_5pct':
        cash_waiting_for_dip = 0.0
        spy_recent_high = price_df['SPY'].iloc[0] if 'SPY' in valid_tickers else 0
        buy_queue = ['SPY', 'QQQ']
        buy_index = 0
        dip_buys = []

    if reinvest_mode == 'drip':
        drip_queue = []  # List of (date, amount) tuples for gradual reinvestment
        drip_cash = 0.0

    if reinvest_mode == 'yield_volatility':
        treasury_cash = 0.0
        TBILL_RATE = 0.04  # Placeholder 4% T-bill rate (should be actual historical data)

    holdings_history = []

    for i, date in enumerate(dates):
        # === REINVESTMENT LOGIC (before trimming) ===

        # Dip-buy reinvestment
        if reinvest_mode == 'dip_buy_5pct' and 'SPY' in valid_tickers:
            current_spy = price_df['SPY'].iloc[i]
            if current_spy > spy_recent_high:
                spy_recent_high = current_spy

            current_drop = (spy_recent_high - current_spy) / spy_recent_high

            if current_drop >= 0.05 and cash_waiting_for_dip > 0:
                next_buy = buy_queue[buy_index]
                if next_buy in valid_tickers:
                    # Apply transaction cost when buying
                    amount_after_buy_cost = cash_waiting_for_dip * (1 - TRANSACTION_COST_PCT)
                    shares_to_buy = amount_after_buy_cost / price_df[next_buy].iloc[i]
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

        # Drip reinvestment (25% per week = 5 trading days)
        if reinvest_mode == 'drip' and drip_cash > 0:
            # Check if volatility has normalized (vol < 1.2x 3-month avg)
            volatility_normalized = False
            if i >= 63 and 'SPY' in valid_tickers:  # 63 days ~3 months
                vol_30_spy = volatility_30['SPY'].iloc[i]
                vol_63_avg = volatility_30['SPY'].iloc[i-63:i].mean()
                if pd.notna(vol_30_spy) and pd.notna(vol_63_avg) and vol_63_avg > 0:
                    volatility_normalized = vol_30_spy < 1.2 * vol_63_avg

            # Reinvest 25% per week (5 days) OR all if volatility normalized
            if i % 5 == 0 or volatility_normalized:
                amount_to_reinvest = drip_cash if volatility_normalized else drip_cash * 0.25

                # Apply transaction cost when buying
                amount_after_buy_cost = amount_to_reinvest * (1 - TRANSACTION_COST_PCT)

                # Reinvest pro-rata across portfolio
                total_value = sum(holdings[t] * price_df[t].iloc[i] for t in valid_tickers)
                for t in valid_tickers:
                    weight = (holdings[t] * price_df[t].iloc[i]) / total_value if total_value > 0 else 1.0/len(valid_tickers)
                    holdings[t] += (amount_after_buy_cost * weight) / price_df[t].iloc[i]

                drip_cash -= amount_to_reinvest

        # Yield/volatility-based reinvestment (GRADUAL to avoid spikes)
        if reinvest_mode == 'yield_volatility' and treasury_cash > 0 and 'SPY' in valid_tickers:
            # Check if volatility normalized
            volatility_normalized = False
            if i >= 63:
                vol_30_spy = volatility_30['SPY'].iloc[i]
                vol_20_avg = volatility_30['SPY'].iloc[i-20:i].mean()
                if pd.notna(vol_30_spy) and pd.notna(vol_20_avg) and vol_20_avg > 0:
                    volatility_normalized = vol_30_spy < vol_20_avg

            # Reinvest GRADUALLY (20% per day when normalized) to avoid massive spikes
            if volatility_normalized and treasury_cash > 100:  # Only if we have meaningful cash
                amount_to_reinvest = treasury_cash * 0.20  # 20% per day

                # Apply transaction cost when buying
                amount_after_buy_cost = amount_to_reinvest * (1 - TRANSACTION_COST_PCT)
                holdings['SPY'] += amount_after_buy_cost / price_df['SPY'].iloc[i]
                treasury_cash -= amount_to_reinvest

        # === TRIM LOGIC ===
        for ticker in valid_tickers:
            if holdings[ticker] <= 0:
                continue

            current_price = price_df[ticker].iloc[i]

            # Determine if we should trim based on strategy type
            should_trim = False

            if strategy_type == 'threshold':
                should_trim = should_trim_threshold(current_price, cost_basis[ticker], threshold)
            elif strategy_type == 'momentum':
                should_trim = should_trim_momentum(ticker, i, price_df, ma_200, momentum_20)
            elif strategy_type == 'volatility':
                should_trim = should_trim_volatility(ticker, i, volatility_30, volatility_252_median,
                                                     threshold,  # vol_threshold
                                                     last_trim_dates, date, trim_active)

            if should_trim:
                shares_to_sell = holdings[ticker] * TRIM_PERCENTAGE
                gross_proceeds = shares_to_sell * current_price

                # Apply transaction cost
                transaction_cost = gross_proceeds * TRANSACTION_COST_PCT
                proceeds_after_cost = gross_proceeds - transaction_cost

                # Calculate capital gain and apply tax
                cost_for_shares_sold = shares_to_sell * cost_basis[ticker]
                capital_gain = proceeds_after_cost - cost_for_shares_sold
                capital_gains_tax = max(0, capital_gain * CAPITAL_GAINS_TAX_RATE)  # Only tax gains, not losses

                # Net proceeds after all costs and taxes
                net_proceeds = proceeds_after_cost - capital_gains_tax

                holdings[ticker] -= shares_to_sell

                trades.append({
                    'date': date,
                    'ticker': ticker,
                    'gross_proceeds': gross_proceeds,
                    'net_proceeds': net_proceeds,
                    'transaction_cost': transaction_cost,
                    'capital_gains_tax': capital_gains_tax,
                    'price': current_price
                })

                # Update last trim date for volatility strategy cooldown
                if strategy_type == 'volatility':
                    last_trim_dates[ticker] = date

                # Allocate proceeds based on reinvestment mode (using net proceeds)
                if reinvest_mode == 'cash':
                    cash += net_proceeds
                elif reinvest_mode == 'dip_buy_5pct':
                    cash_waiting_for_dip += net_proceeds
                elif reinvest_mode == 'drip':
                    drip_cash += net_proceeds
                elif reinvest_mode == 'yield_volatility':
                    treasury_cash += net_proceeds
                elif reinvest_mode == 'spy' and 'SPY' in valid_tickers:
                    # Apply transaction cost when buying
                    amount_after_buy_cost = net_proceeds * (1 - TRANSACTION_COST_PCT)
                    holdings['SPY'] += amount_after_buy_cost / price_df['SPY'].iloc[i]
                elif reinvest_mode == 'pro_rata':
                    # Apply transaction cost when buying
                    amount_after_buy_cost = net_proceeds * (1 - TRANSACTION_COST_PCT)
                    total_value = sum(holdings[t] * price_df[t].iloc[i] for t in valid_tickers)
                    for t in valid_tickers:
                        weight = (holdings[t] * price_df[t].iloc[i]) / total_value if total_value > 0 else 1.0/len(valid_tickers)
                        holdings[t] += (amount_after_buy_cost * weight) / price_df[t].iloc[i]

                # Reset cost basis for threshold strategies
                if strategy_type == 'threshold':
                    cost_basis[ticker] = current_price * 1.05

        holdings_history.append(holdings.copy())

    # Calculate portfolio value
    portfolio_value_df = pd.DataFrame(holdings_history, index=dates)

    # Add cash column (different types of cash for different modes)
    if reinvest_mode == 'dip_buy_5pct':
        portfolio_value_df['Cash'] = cash_waiting_for_dip
    elif reinvest_mode == 'drip':
        portfolio_value_df['Cash'] = drip_cash
    elif reinvest_mode == 'yield_volatility':
        portfolio_value_df['Cash'] = treasury_cash
    else:
        portfolio_value_df['Cash'] = cash

    portfolio_value_df['Total_Value'] = sum(portfolio_value_df[ticker] * price_df[ticker] for ticker in valid_tickers) + portfolio_value_df['Cash']

    # Calculate metrics
    metrics = calculate_metrics(portfolio_value_df['Total_Value'], INITIAL_CASH)
    metrics['final_value'] = portfolio_value_df['Total_Value'].iloc[-1]
    metrics['num_trades'] = len(trades)
    metrics['cash_held'] = portfolio_value_df['Cash'].iloc[-1]

    # Calculate total costs and taxes paid
    total_transaction_costs = sum(trade['transaction_cost'] for trade in trades)
    total_capital_gains_tax = sum(trade['capital_gains_tax'] for trade in trades)
    metrics['total_transaction_costs'] = total_transaction_costs
    metrics['total_capital_gains_tax'] = total_capital_gains_tax
    metrics['total_costs_and_taxes'] = total_transaction_costs + total_capital_gains_tax

    # Add mode-specific metrics
    if reinvest_mode == 'dip_buy_5pct':
        metrics['num_dip_buys'] = len(dip_buys)
        metrics['avg_dip_size'] = np.mean([d['spy_drop_pct'] for d in dip_buys]) if dip_buys else 0

    return metrics

# ============================================================================
# RUN ALL STRATEGIES
# ============================================================================

print("\n" + "="*80)
print("RUNNING BACKTESTS - INDEX-FOCUSED PORTFOLIO")
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

# === RUN ALL TRIMMING STRATEGIES ===
strategy_count = 0
total_strategies = (
    len(TRIM_THRESHOLDS) * len(REINVEST_MODES) +  # threshold strategies
    1 * len(REINVEST_MODES) +  # momentum (1 variant)
    len(VOLATILITY_THRESHOLDS) * len(REINVEST_MODES)  # volatility (3 thresholds)
)

for strategy_type in TRIM_STRATEGIES:
    # Determine strategy variants
    if strategy_type == 'threshold':
        strategy_params = TRIM_THRESHOLDS
    elif strategy_type == 'volatility':
        strategy_params = VOLATILITY_THRESHOLDS  # Test 1.5x, 2.0x, 2.5x
    else:  # momentum
        strategy_params = [None]

    for param in strategy_params:
        for mode in REINVEST_MODES:
            strategy_count += 1

            # Generate strategy name
            if strategy_type == 'threshold':
                strategy_name = f"Trim@+{int(param*100)}% ({mode.replace('_', '-')})"
            elif strategy_type == 'momentum':
                strategy_name = f"Momentum-Guided ({mode.replace('_', '-')})"
            elif strategy_type == 'volatility':
                strategy_name = f"Volatility-{param}x ({mode.replace('_', '-')})"

            print(f"\n🔄 Running [{strategy_count}/{total_strategies}]: {strategy_name}...")

            # Run the strategy
            metrics = run_single_strategy(
                strategy_type=strategy_type,
                threshold=param,
                reinvest_mode=mode,
                price_df=price_df,
                dates=dates,
                valid_tickers=valid_tickers,
                initial_shares=initial_shares,
                ma_200=ma_200,
                momentum_20=momentum_20,
                volatility_30=volatility_30,
                volatility_252_median=volatility_252_median
            )

            all_results[strategy_name] = metrics

            print(f"  ✓ Final Value: ${metrics['final_value']:,.2f}")
            print(f"  ✓ CAGR: {metrics['cagr']:.2%}")
            print(f"  ✓ Trims: {metrics['num_trades']}")
            if 'num_dip_buys' in metrics:
                print(f"  ✓ Dip Buys: {metrics['num_dip_buys']}")

print("\n" + "="*80)
print("✅ INDEX-FOCUSED BACKTEST COMPLETE")
print("="*80)

# Create comparison
comparison_df = pd.DataFrame(all_results).T
comparison_df = comparison_df.sort_values('final_value', ascending=False)

print("\n🏆 TOP 5 STRATEGIES (INDEX-FOCUSED PORTFOLIO):\n")
print(comparison_df.head(5)[['final_value', 'cagr', 'sharpe_ratio', 'max_drawdown']].to_string())

dip_strategies = [s for s in comparison_df.index if 'dip-buy' in s]
if dip_strategies:
    print("\n💡 DIP-BUY STRATEGIES (INDEX-FOCUSED):\n")
    print(comparison_df.loc[dip_strategies][['final_value', 'cagr', 'num_trades', 'num_dip_buys']].to_string())

# Compare to original backtest
print("\n" + "="*80)
print("COMPARISON: INDEX-FOCUSED vs ORIGINAL (NVDA-dominated)")
print("="*80)

print("\nOriginal backtest (with NVDA at $0.48):")
print("  Buy-and-Hold: $5,430,469 (50.14% CAGR)")
print("  Winner: Buy-and-Hold (NVDA contributed ~$4.5M)")

bh_metrics = all_results['Buy-and-Hold']
print(f"\nIndex-focused backtest (realistic portfolio):")
print(f"  Buy-and-Hold: ${bh_metrics['final_value']:,.2f} ({bh_metrics['cagr']:.2%} CAGR)")
print(f"  Winner: {comparison_df.index[0]}")

winner = comparison_df.iloc[0]
if comparison_df.index[0] != 'Buy-and-Hold':
    print(f"\n🎉 TRIMMING WINS with realistic portfolio!")
    print(f"  {comparison_df.index[0]}: ${winner['final_value']:,.2f} ({winner['cagr']:.2%} CAGR)")
    print(f"  Beat B&H by: ${winner['final_value'] - bh_metrics['final_value']:,.2f}")
else:
    print(f"\n📊 Buy-and-hold still wins, but by how much?")
    second_place = comparison_df.iloc[1]
    print(f"  Best trim: {comparison_df.index[1]} - ${second_place['final_value']:,.2f}")
    print(f"  Difference: ${bh_metrics['final_value'] - second_place['final_value']:,.2f}")

comparison_df.to_csv(f'{results_dir}/index_focus_results.csv')

print(f"\n✓ Results saved to: {results_dir}/index_focus_results.csv")
print("\n✨ This represents a REALISTIC scenario!")
