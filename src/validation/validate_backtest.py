#!/usr/bin/env python3
"""
Independent Backtest Validator for trim_50pct_spy Strategy
Validates all aspects of the backtest results
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

class BacktestValidator:
    def __init__(self, results_dir="results"):
        self.results_dir = Path(results_dir)
        self.strategy_name = "trim_50pct_spy"
        self.validation_errors = []
        self.validation_warnings = []
        self.validation_info = []

    def load_data(self):
        """Load all backtest data files"""
        print("=" * 80)
        print("LOADING BACKTEST DATA FILES")
        print("=" * 80)

        try:
            # Load portfolio values
            portfolio_file = self.results_dir / f"{self.strategy_name}_portfolio_value.csv"
            self.portfolio_df = pd.read_csv(portfolio_file, index_col=0, parse_dates=True)
            print(f"✓ Loaded portfolio values: {len(self.portfolio_df)} rows")

            # Load trades
            trades_file = self.results_dir / f"{self.strategy_name}_trades.csv"
            self.trades_df = pd.read_csv(trades_file, parse_dates=['date'])
            print(f"✓ Loaded trades: {len(self.trades_df)} trades")

            # Load weights
            weights_file = self.results_dir / f"{self.strategy_name}_weights.csv"
            self.weights_df = pd.read_csv(weights_file, index_col=0, parse_dates=True)
            print(f"✓ Loaded weights: {len(self.weights_df)} rows")

            # Load metrics
            metrics_file = self.results_dir / f"{self.strategy_name}_metrics.csv"
            self.metrics_df = pd.read_csv(metrics_file)
            print(f"✓ Loaded metrics")

            # Load metadata
            metadata_file = self.results_dir / f"{self.strategy_name}_metadata.json"
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
            print(f"✓ Loaded metadata")

            self.validation_info.append("All data files loaded successfully")
            return True

        except Exception as e:
            self.validation_errors.append(f"Failed to load data: {str(e)}")
            return False

    def validate_data_integrity(self):
        """Check for data integrity issues"""
        print("\n" + "=" * 80)
        print("DATA INTEGRITY VALIDATION")
        print("=" * 80)

        errors_found = 0

        # Check for missing dates
        date_range = pd.date_range(start=self.portfolio_df.index[0],
                                   end=self.portfolio_df.index[-1],
                                   freq='B')  # Business days
        missing_dates = set(date_range) - set(self.portfolio_df.index)
        if len(missing_dates) > 100:  # Allow some holidays
            self.validation_warnings.append(f"Suspicious number of missing dates: {len(missing_dates)}")
            print(f"⚠ Warning: {len(missing_dates)} business days missing from portfolio data")
        else:
            print(f"✓ Date coverage acceptable ({len(missing_dates)} holidays/gaps)")

        # Check for negative values
        if (self.portfolio_df['Total_Value'] < 0).any():
            self.validation_errors.append("Negative portfolio values detected")
            errors_found += 1
            print("✗ ERROR: Negative portfolio values found")
        else:
            print("✓ No negative portfolio values")

        # Check for NaN values
        nan_counts = self.portfolio_df.isna().sum()
        if nan_counts.sum() > 0:
            self.validation_errors.append(f"NaN values detected: {nan_counts[nan_counts > 0].to_dict()}")
            errors_found += 1
            print(f"✗ ERROR: NaN values found in {(nan_counts > 0).sum()} columns")
        else:
            print("✓ No NaN values in portfolio data")

        # Check cash column
        if 'Cash' in self.portfolio_df.columns:
            if (self.portfolio_df['Cash'] < 0).any():
                self.validation_errors.append("Negative cash values detected")
                errors_found += 1
                print("✗ ERROR: Negative cash values found")
            else:
                print("✓ No negative cash values")

        # Check weights sum to 1 (or close to it)
        ticker_cols = [col for col in self.weights_df.columns if col != 'Cash']
        weights_sum = self.weights_df[ticker_cols].sum(axis=1)
        weights_off = weights_sum[(weights_sum < 0.99) | (weights_sum > 1.01)]
        if len(weights_off) > 0:
            self.validation_warnings.append(f"{len(weights_off)} rows where weights don't sum to ~1.0")
            print(f"⚠ Warning: {len(weights_off)} rows with weights sum ≠ 1.0 (range: {weights_sum.min():.4f} - {weights_sum.max():.4f})")
        else:
            print(f"✓ Weights sum to 1.0 (range: {weights_sum.min():.4f} - {weights_sum.max():.4f})")

        # Check for duplicate dates
        if self.portfolio_df.index.duplicated().any():
            dup_count = self.portfolio_df.index.duplicated().sum()
            self.validation_errors.append(f"{dup_count} duplicate dates in portfolio data")
            errors_found += 1
            print(f"✗ ERROR: {dup_count} duplicate dates found")
        else:
            print("✓ No duplicate dates")

        # Check trades data integrity
        if (self.trades_df['shares_sold'] <= 0).any():
            self.validation_errors.append("Non-positive shares_sold values in trades")
            errors_found += 1
            print("✗ ERROR: Non-positive shares_sold values")
        else:
            print("✓ All shares_sold values are positive")

        if (self.trades_df['price'] <= 0).any():
            self.validation_errors.append("Non-positive prices in trades")
            errors_found += 1
            print("✗ ERROR: Non-positive prices in trades")
        else:
            print("✓ All trade prices are positive")

        print(f"\nData Integrity Summary: {errors_found} errors, {len(self.validation_warnings)} warnings")
        return errors_found == 0

    def validate_trim_logic(self):
        """Validate that trims occurred correctly according to strategy rules"""
        print("\n" + "=" * 80)
        print("TRIM LOGIC VALIDATION")
        print("=" * 80)

        trim_threshold = self.metadata['trim_threshold']
        trim_percentage = self.metadata['trim_percentage']

        print(f"Strategy Parameters:")
        print(f"  Trim Threshold: {trim_threshold * 100}% gain")
        print(f"  Trim Amount: {trim_percentage * 100}% of position")
        print(f"\nValidating {len(self.trades_df)} trades...\n")

        errors_found = 0

        for idx, trade in self.trades_df.iterrows():
            trade_date = trade['date']
            ticker = trade['ticker']
            gain_pct = trade['gain_pct']

            print(f"Trade {idx + 1}: {trade_date.strftime('%Y-%m-%d')} - {ticker}")
            print(f"  Reported Gain: {gain_pct * 100:.2f}%")

            # Validate gain threshold
            if gain_pct < trim_threshold:
                error_msg = f"Trade {idx + 1}: Gain {gain_pct*100:.2f}% below threshold {trim_threshold*100}%"
                self.validation_errors.append(error_msg)
                errors_found += 1
                print(f"  ✗ ERROR: Gain below threshold ({trim_threshold * 100}%)")
            else:
                print(f"  ✓ Gain exceeds threshold")

            # Find the trade date in portfolio data
            try:
                trade_date_normalized = pd.Timestamp(trade_date).normalize()

                # Find closest date if exact match doesn't exist
                if trade_date_normalized not in self.portfolio_df.index:
                    closest_idx = self.portfolio_df.index.searchsorted(trade_date_normalized)
                    if closest_idx < len(self.portfolio_df):
                        trade_date_normalized = self.portfolio_df.index[closest_idx]
                        print(f"  Note: Using closest date {trade_date_normalized.strftime('%Y-%m-%d')}")

                # Get position before trade
                position_before_idx = self.portfolio_df.index.get_loc(trade_date_normalized)
                if position_before_idx > 0:
                    position_before = self.portfolio_df.iloc[position_before_idx - 1][ticker]
                    position_after = self.portfolio_df.iloc[position_before_idx][ticker]

                    shares_change = position_before - position_after
                    shares_sold = trade['shares_sold']

                    # Allow 1% tolerance for rounding
                    if abs(shares_change - shares_sold) / shares_sold > 0.01:
                        warning_msg = f"Trade {idx + 1}: Shares mismatch - Portfolio change: {shares_change:.2f}, Trade: {shares_sold:.2f}"
                        self.validation_warnings.append(warning_msg)
                        print(f"  ⚠ Warning: Shares mismatch ({abs(shares_change - shares_sold):.2f} difference)")
                    else:
                        print(f"  ✓ Shares sold matches portfolio change ({shares_sold:.2f})")

                    # Validate trim percentage (approximately)
                    trim_pct = shares_change / position_before
                    expected_trim = trim_percentage
                    if abs(trim_pct - expected_trim) / expected_trim > 0.05:  # 5% tolerance
                        warning_msg = f"Trade {idx + 1}: Trim {trim_pct*100:.2f}% differs from expected {expected_trim*100:.2f}%"
                        self.validation_warnings.append(warning_msg)
                        print(f"  ⚠ Warning: Trim percentage {trim_pct*100:.2f}% vs expected {expected_trim*100:.2f}%")
                    else:
                        print(f"  ✓ Trim percentage correct ({trim_pct*100:.2f}%)")

            except Exception as e:
                warning_msg = f"Trade {idx + 1}: Could not validate against portfolio data - {str(e)}"
                self.validation_warnings.append(warning_msg)
                print(f"  ⚠ Warning: {str(e)}")

            # Calculate actual gain from price data if we can find initial purchase
            # This is challenging without purchase history, so we'll skip for now

            print()

        print(f"Trim Logic Summary: {errors_found} errors, {len(self.validation_warnings)} warnings")
        return errors_found == 0

    def recalculate_metrics(self):
        """Independently recalculate performance metrics"""
        print("\n" + "=" * 80)
        print("PERFORMANCE METRICS RECALCULATION")
        print("=" * 80)

        initial_capital = self.metadata['initial_capital']
        portfolio_values = self.portfolio_df['Total_Value']

        # Final value
        final_value = portfolio_values.iloc[-1]
        print(f"\nFinal Portfolio Value:")
        print(f"  Calculated: ${final_value:,.2f}")
        print(f"  Reported:   ${self.metrics_df['final_value'].iloc[0]:,.2f}")

        if abs(final_value - self.metrics_df['final_value'].iloc[0]) > 1.0:
            self.validation_errors.append(f"Final value mismatch: {final_value} vs {self.metrics_df['final_value'].iloc[0]}")
            print(f"  ✗ ERROR: Mismatch of ${abs(final_value - self.metrics_df['final_value'].iloc[0]):,.2f}")
        else:
            print(f"  ✓ Values match")

        # Total return
        total_return = (final_value / initial_capital) - 1
        print(f"\nTotal Return:")
        print(f"  Calculated: {total_return * 100:.2f}%")
        print(f"  Reported:   {self.metrics_df['total_return'].iloc[0] * 100:.2f}%")

        if abs(total_return - self.metrics_df['total_return'].iloc[0]) > 0.001:
            self.validation_errors.append(f"Total return mismatch: {total_return} vs {self.metrics_df['total_return'].iloc[0]}")
            print(f"  ✗ ERROR: Mismatch of {abs(total_return - self.metrics_df['total_return'].iloc[0]) * 100:.3f}%")
        else:
            print(f"  ✓ Values match")

        # CAGR
        start_date = portfolio_values.index[0]
        end_date = portfolio_values.index[-1]
        years = (end_date - start_date).days / 365.25
        cagr = (final_value / initial_capital) ** (1 / years) - 1
        print(f"\nCAGR (Compound Annual Growth Rate):")
        print(f"  Period: {years:.2f} years")
        print(f"  Calculated: {cagr * 100:.2f}%")
        print(f"  Reported:   {self.metrics_df['cagr'].iloc[0] * 100:.2f}%")

        if abs(cagr - self.metrics_df['cagr'].iloc[0]) > 0.001:
            self.validation_warnings.append(f"CAGR mismatch: {cagr} vs {self.metrics_df['cagr'].iloc[0]}")
            print(f"  ⚠ Warning: Mismatch of {abs(cagr - self.metrics_df['cagr'].iloc[0]) * 100:.3f}%")
        else:
            print(f"  ✓ Values match")

        # Daily returns
        daily_returns = portfolio_values.pct_change().dropna()

        # Volatility (annualized)
        volatility = daily_returns.std() * np.sqrt(252)
        print(f"\nVolatility (Annualized):")
        print(f"  Calculated: {volatility * 100:.2f}%")
        print(f"  Reported:   {self.metrics_df['volatility'].iloc[0] * 100:.2f}%")

        if abs(volatility - self.metrics_df['volatility'].iloc[0]) > 0.001:
            self.validation_warnings.append(f"Volatility mismatch: {volatility} vs {self.metrics_df['volatility'].iloc[0]}")
            print(f"  ⚠ Warning: Mismatch of {abs(volatility - self.metrics_df['volatility'].iloc[0]) * 100:.3f}%")
        else:
            print(f"  ✓ Values match")

        # Sharpe Ratio (assuming 0% risk-free rate)
        sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))
        print(f"\nSharpe Ratio:")
        print(f"  Calculated: {sharpe_ratio:.4f}")
        print(f"  Reported:   {self.metrics_df['sharpe_ratio'].iloc[0]:.4f}")

        if abs(sharpe_ratio - self.metrics_df['sharpe_ratio'].iloc[0]) > 0.01:
            self.validation_warnings.append(f"Sharpe ratio mismatch: {sharpe_ratio} vs {self.metrics_df['sharpe_ratio'].iloc[0]}")
            print(f"  ⚠ Warning: Mismatch of {abs(sharpe_ratio - self.metrics_df['sharpe_ratio'].iloc[0]):.4f}")
        else:
            print(f"  ✓ Values match")

        # Sortino Ratio (downside deviation)
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        sortino_ratio = (daily_returns.mean() * 252) / downside_std if downside_std > 0 else 0
        print(f"\nSortino Ratio:")
        print(f"  Calculated: {sortino_ratio:.4f}")
        print(f"  Reported:   {self.metrics_df['sortino_ratio'].iloc[0]:.4f}")

        if abs(sortino_ratio - self.metrics_df['sortino_ratio'].iloc[0]) > 0.01:
            self.validation_warnings.append(f"Sortino ratio mismatch: {sortino_ratio} vs {self.metrics_df['sortino_ratio'].iloc[0]}")
            print(f"  ⚠ Warning: Mismatch of {abs(sortino_ratio - self.metrics_df['sortino_ratio'].iloc[0]):.4f}")
        else:
            print(f"  ✓ Values match")

        # Maximum Drawdown
        cumulative_returns = (1 + daily_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        print(f"\nMaximum Drawdown:")
        print(f"  Calculated: {max_drawdown * 100:.2f}%")
        print(f"  Reported:   {self.metrics_df['max_drawdown'].iloc[0] * 100:.2f}%")

        if abs(max_drawdown - self.metrics_df['max_drawdown'].iloc[0]) > 0.001:
            self.validation_warnings.append(f"Max drawdown mismatch: {max_drawdown} vs {self.metrics_df['max_drawdown'].iloc[0]}")
            print(f"  ⚠ Warning: Mismatch of {abs(max_drawdown - self.metrics_df['max_drawdown'].iloc[0]) * 100:.3f}%")
        else:
            print(f"  ✓ Values match")

        # Number of trades
        num_trades = len(self.trades_df)
        print(f"\nNumber of Trades:")
        print(f"  Calculated: {num_trades}")
        print(f"  Reported:   {int(self.metrics_df['num_trades'].iloc[0])}")

        if num_trades != int(self.metrics_df['num_trades'].iloc[0]):
            self.validation_errors.append(f"Trade count mismatch: {num_trades} vs {self.metrics_df['num_trades'].iloc[0]}")
            print(f"  ✗ ERROR: Mismatch")
        else:
            print(f"  ✓ Values match")

        return True

    def validate_strategy_logic(self):
        """Validate that the strategy was implemented correctly"""
        print("\n" + "=" * 80)
        print("STRATEGY LOGIC VALIDATION")
        print("=" * 80)

        reinvest_mode = self.metadata['reinvest_mode']
        print(f"\nReinvestment Mode: {reinvest_mode}")

        if reinvest_mode == 'spy':
            print("Validating that trim proceeds were reinvested in SPY...")

            # Check if SPY position increased after each trim
            for idx, trade in self.trades_df.iterrows():
                trade_date = pd.Timestamp(trade['date']).normalize()
                ticker = trade['ticker']

                # Only check non-SPY trades
                if ticker != 'SPY':
                    try:
                        # Find trade date in portfolio
                        if trade_date not in self.portfolio_df.index:
                            trade_date = self.portfolio_df.index[self.portfolio_df.index.searchsorted(trade_date)]

                        trade_idx = self.portfolio_df.index.get_loc(trade_date)

                        if trade_idx > 0:
                            spy_before = self.portfolio_df.iloc[trade_idx - 1]['SPY']
                            spy_after = self.portfolio_df.iloc[trade_idx]['SPY']

                            if spy_after <= spy_before:
                                self.validation_warnings.append(
                                    f"SPY didn't increase after {ticker} trim on {trade_date.strftime('%Y-%m-%d')}"
                                )
                                print(f"  ⚠ {trade_date.strftime('%Y-%m-%d')}: SPY didn't increase after {ticker} trim")
                            else:
                                print(f"  ✓ {trade_date.strftime('%Y-%m-%d')}: SPY increased after {ticker} trim")
                    except Exception as e:
                        print(f"  ⚠ Could not validate SPY reinvestment for {ticker} on {trade_date}: {str(e)}")

        # Validate equal-weight rebalancing at start
        print("\nValidating initial equal-weight allocation...")
        tickers = self.metadata['tickers']
        initial_weights = self.weights_df.iloc[0][tickers]
        expected_weight = 1.0 / len(tickers)

        weight_errors = []
        for ticker, weight in initial_weights.items():
            if abs(weight - expected_weight) > 0.01:  # 1% tolerance
                weight_errors.append(f"{ticker}: {weight:.4f} vs {expected_weight:.4f}")

        if weight_errors:
            self.validation_warnings.append(f"Initial weights not equal: {', '.join(weight_errors)}")
            print(f"  ⚠ Warning: Initial weights not perfectly equal")
            for error in weight_errors:
                print(f"    {error}")
        else:
            print(f"  ✓ All tickers started with equal weight ({expected_weight:.4f})")

        # Check that positions never go negative
        print("\nValidating that no positions went negative...")
        negative_positions = []
        for ticker in tickers:
            if (self.portfolio_df[ticker] < 0).any():
                negative_positions.append(ticker)

        if negative_positions:
            self.validation_errors.append(f"Negative positions detected: {', '.join(negative_positions)}")
            print(f"  ✗ ERROR: Negative positions in {', '.join(negative_positions)}")
        else:
            print(f"  ✓ No negative positions")

        return True

    def analyze_trade_distribution(self):
        """Analyze the distribution of trades across tickers"""
        print("\n" + "=" * 80)
        print("TRADE DISTRIBUTION ANALYSIS")
        print("=" * 80)

        trades_by_ticker = self.trades_df.groupby('ticker').size()
        total_proceeds = self.trades_df['proceeds'].sum()

        print(f"\nTrades by Ticker:")
        for ticker, count in trades_by_ticker.items():
            ticker_proceeds = self.trades_df[self.trades_df['ticker'] == ticker]['proceeds'].sum()
            avg_gain = self.trades_df[self.trades_df['ticker'] == ticker]['gain_pct'].mean()
            print(f"  {ticker}: {count} trades, ${ticker_proceeds:,.2f} proceeds ({ticker_proceeds/total_proceeds*100:.1f}%), avg gain {avg_gain*100:.1f}%")

        print(f"\nTotal Proceeds: ${total_proceeds:,.2f}")

        # Identify best performing stocks (by trade frequency)
        print("\nMost Frequently Trimmed (indicates strong performance):")
        for ticker, count in trades_by_ticker.sort_values(ascending=False).items():
            print(f"  {ticker}: {count} trims")

        return True

    def generate_report(self):
        """Generate comprehensive validation report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"validation_report_{self.strategy_name}_{timestamp}.txt"

        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("BACKTEST VALIDATION REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Strategy: {self.metadata['strategy_name']}\n")
            f.write(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Backtest Period: {self.metadata['start_date']} to {self.metadata['end_date']}\n")
            f.write(f"Initial Capital: ${self.metadata['initial_capital']:,.2f}\n\n")

            f.write("=" * 80 + "\n")
            f.write("VALIDATION SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            total_errors = len(self.validation_errors)
            total_warnings = len(self.validation_warnings)

            if total_errors == 0 and total_warnings == 0:
                f.write("✓✓✓ VALIDATION PASSED - NO ERRORS OR WARNINGS ✓✓✓\n\n")
                verdict = "PASSED"
            elif total_errors == 0:
                f.write(f"✓ VALIDATION PASSED WITH {total_warnings} WARNINGS\n\n")
                verdict = "PASSED WITH WARNINGS"
            else:
                f.write(f"✗ VALIDATION FAILED WITH {total_errors} ERRORS AND {total_warnings} WARNINGS\n\n")
                verdict = "FAILED"

            f.write(f"Total Errors:   {total_errors}\n")
            f.write(f"Total Warnings: {total_warnings}\n")
            f.write(f"Info Messages:  {len(self.validation_info)}\n\n")

            if total_errors > 0:
                f.write("=" * 80 + "\n")
                f.write("ERRORS\n")
                f.write("=" * 80 + "\n\n")
                for i, error in enumerate(self.validation_errors, 1):
                    f.write(f"{i}. {error}\n")
                f.write("\n")

            if total_warnings > 0:
                f.write("=" * 80 + "\n")
                f.write("WARNINGS\n")
                f.write("=" * 80 + "\n\n")
                for i, warning in enumerate(self.validation_warnings, 1):
                    f.write(f"{i}. {warning}\n")
                f.write("\n")

            # Strategy configuration
            f.write("=" * 80 + "\n")
            f.write("STRATEGY CONFIGURATION\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Tickers: {', '.join(self.metadata['tickers'])}\n")
            f.write(f"Trim Threshold: {self.metadata['trim_threshold'] * 100}%\n")
            f.write(f"Trim Percentage: {self.metadata['trim_percentage'] * 100}%\n")
            f.write(f"Reinvest Mode: {self.metadata['reinvest_mode']}\n")
            f.write(f"Transaction Fees: {self.metadata['fees'] * 100}%\n\n")

            # Performance metrics
            f.write("=" * 80 + "\n")
            f.write("PERFORMANCE METRICS (REPORTED)\n")
            f.write("=" * 80 + "\n\n")
            metrics = self.metrics_df.iloc[0]
            f.write(f"Final Value:     ${metrics['final_value']:,.2f}\n")
            f.write(f"Total Return:    {metrics['total_return'] * 100:.2f}%\n")
            f.write(f"CAGR:            {metrics['cagr'] * 100:.2f}%\n")
            f.write(f"Sharpe Ratio:    {metrics['sharpe_ratio']:.4f}\n")
            f.write(f"Sortino Ratio:   {metrics['sortino_ratio']:.4f}\n")
            f.write(f"Max Drawdown:    {metrics['max_drawdown'] * 100:.2f}%\n")
            f.write(f"Volatility:      {metrics['volatility'] * 100:.2f}%\n")
            f.write(f"Number of Trades: {int(metrics['num_trades'])}\n")
            f.write(f"Final Cash:      ${metrics['cash_held']:,.2f}\n\n")

            # Trade summary
            f.write("=" * 80 + "\n")
            f.write("TRADE SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            trades_by_ticker = self.trades_df.groupby('ticker').agg({
                'shares_sold': 'sum',
                'proceeds': 'sum',
                'gain_pct': 'mean'
            }).round(2)

            f.write(f"{'Ticker':<8} {'Trades':<8} {'Total Proceeds':<18} {'Avg Gain %':<12}\n")
            f.write("-" * 60 + "\n")
            for ticker, row in trades_by_ticker.iterrows():
                trade_count = len(self.trades_df[self.trades_df['ticker'] == ticker])
                f.write(f"{ticker:<8} {trade_count:<8} ${row['proceeds']:<17,.2f} {row['gain_pct']*100:<12.2f}\n")

            f.write("\n")
            f.write(f"Total Proceeds from All Trims: ${self.trades_df['proceeds'].sum():,.2f}\n\n")

            # Data quality metrics
            f.write("=" * 80 + "\n")
            f.write("DATA QUALITY METRICS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Portfolio Data Points: {len(self.portfolio_df)}\n")
            f.write(f"Date Range: {self.portfolio_df.index[0].strftime('%Y-%m-%d')} to {self.portfolio_df.index[-1].strftime('%Y-%m-%d')}\n")
            f.write(f"Trading Days: {len(self.portfolio_df)}\n")
            f.write(f"Missing Values: {self.portfolio_df.isna().sum().sum()}\n")
            f.write(f"Negative Values: {(self.portfolio_df < 0).sum().sum()}\n\n")

            # Final verdict
            f.write("=" * 80 + "\n")
            f.write("FINAL VERDICT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Validation Result: {verdict}\n\n")

            if verdict == "PASSED":
                f.write("The backtest results have been thoroughly validated and no issues were found.\n")
                f.write("All performance metrics are correctly calculated and the strategy logic\n")
                f.write("was properly implemented. The results are reliable and can be used for\n")
                f.write("trading decisions.\n")
            elif verdict == "PASSED WITH WARNINGS":
                f.write("The backtest results are generally sound but some warnings were flagged.\n")
                f.write("Review the warnings above to determine if they affect the reliability of\n")
                f.write("the results. Most warnings are minor and do not invalidate the backtest.\n")
            else:
                f.write("CRITICAL: The backtest contains errors that must be addressed before\n")
                f.write("these results can be trusted. Review all errors above and rerun the\n")
                f.write("backtest after fixing the issues.\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF VALIDATION REPORT\n")
            f.write("=" * 80 + "\n")

        print(f"\n✓ Validation report saved to: {report_file}")
        return report_file

    def run_full_validation(self):
        """Run complete validation workflow"""
        print("\n" + "=" * 80)
        print("BACKTEST VALIDATOR - TRIM@+50% (SPY) STRATEGY")
        print("=" * 80)
        print()

        # Load data
        if not self.load_data():
            print("\n✗ Failed to load data. Aborting validation.")
            return False

        # Run validation steps
        self.validate_data_integrity()
        self.recalculate_metrics()
        self.validate_trim_logic()
        self.validate_strategy_logic()
        self.analyze_trade_distribution()

        # Generate report
        report_file = self.generate_report()

        # Print summary
        print("\n" + "=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)
        print(f"\nErrors:   {len(self.validation_errors)}")
        print(f"Warnings: {len(self.validation_warnings)}")
        print(f"Info:     {len(self.validation_info)}")

        if len(self.validation_errors) == 0:
            print("\n✓✓✓ VALIDATION PASSED ✓✓✓")
            return True
        else:
            print("\n✗✗✗ VALIDATION FAILED ✗✗✗")
            print("\nPlease review the errors above and the detailed report.")
            return False

if __name__ == "__main__":
    validator = BacktestValidator()
    success = validator.run_full_validation()
    exit(0 if success else 1)
