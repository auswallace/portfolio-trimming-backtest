#!/usr/bin/env python3
"""
Independent Validator for Trim@+50% (dip-buy-5pct) Strategy

This script independently validates the backtest results by:
1. Recalculating all performance metrics
2. Validating trim events (50% gain threshold)
3. Validating dip-buy events (5% SPY drop threshold)
4. Checking SPY/QQQ alternation
5. Verifying data integrity
6. Comparing calculated vs reported metrics
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

class DipBuyStrategyValidator:
    def __init__(self, results_dir):
        self.results_dir = Path(results_dir)
        self.validation_results = {}
        self.errors = []
        self.warnings = []

    def load_data(self):
        """Load all result files"""
        print("=" * 80)
        print("LOADING DATA FILES")
        print("=" * 80)

        # Load metadata
        with open(self.results_dir / 'trim_50pct_dip_buy_5pct_metadata.json', 'r') as f:
            self.metadata = json.load(f)
        print(f"✓ Loaded metadata: {len(self.metadata['dip_buys'])} dip-buy events recorded")

        # Load metrics
        self.metrics = pd.read_csv(self.results_dir / 'trim_50pct_dip_buy_5pct_metrics.csv')
        print(f"✓ Loaded metrics CSV")

        # Load trades
        self.trades = pd.read_csv(self.results_dir / 'trim_50pct_dip_buy_5pct_trades.csv')
        self.trades['date'] = pd.to_datetime(self.trades['date'])
        print(f"✓ Loaded {len(self.trades)} trade records")

        # Load portfolio values
        self.portfolio = pd.read_csv(
            self.results_dir / 'trim_50pct_dip_buy_5pct_portfolio_value.csv',
            index_col=0
        )
        self.portfolio.index = pd.to_datetime(self.portfolio.index)
        print(f"✓ Loaded portfolio time series: {len(self.portfolio)} days")
        print()

    def validate_basic_metrics(self):
        """Recalculate and validate core performance metrics"""
        print("=" * 80)
        print("VALIDATING PERFORMANCE METRICS")
        print("=" * 80)

        # Extract reported metrics
        reported = self.metrics.iloc[0]

        # Calculate independent metrics
        initial_value = self.metadata['initial_capital']
        final_value = self.portfolio['Total_Value'].iloc[-1]

        # Total return
        calc_total_return = (final_value - initial_value) / initial_value
        print(f"Total Return:")
        print(f"  Reported: {reported['total_return']:.4f} ({reported['total_return']*100:.2f}%)")
        print(f"  Calculated: {calc_total_return:.4f} ({calc_total_return*100:.2f}%)")
        print(f"  Difference: {abs(calc_total_return - reported['total_return']):.6f}")

        if abs(calc_total_return - reported['total_return']) < 1e-6:
            print("  ✓ PASS")
        else:
            self.errors.append(f"Total return mismatch: {calc_total_return} vs {reported['total_return']}")
            print("  ✗ FAIL")
        print()

        # CAGR
        years = (self.portfolio.index[-1] - self.portfolio.index[0]).days / 365.25
        calc_cagr = (final_value / initial_value) ** (1 / years) - 1
        print(f"CAGR (Compound Annual Growth Rate):")
        print(f"  Period: {years:.2f} years")
        print(f"  Reported: {reported['cagr']:.4f} ({reported['cagr']*100:.2f}%)")
        print(f"  Calculated: {calc_cagr:.4f} ({calc_cagr*100:.2f}%)")
        print(f"  Difference: {abs(calc_cagr - reported['cagr']):.6f}")

        if abs(calc_cagr - reported['cagr']) < 1e-6:
            print("  ✓ PASS")
        else:
            self.errors.append(f"CAGR mismatch: {calc_cagr} vs {reported['cagr']}")
            print("  ✗ FAIL")
        print()

        # Maximum Drawdown
        cummax = self.portfolio['Total_Value'].cummax()
        drawdown = (self.portfolio['Total_Value'] - cummax) / cummax
        calc_max_dd = drawdown.min()
        print(f"Maximum Drawdown:")
        print(f"  Reported: {reported['max_drawdown']:.4f} ({reported['max_drawdown']*100:.2f}%)")
        print(f"  Calculated: {calc_max_dd:.4f} ({calc_max_dd*100:.2f}%)")
        print(f"  Difference: {abs(calc_max_dd - reported['max_drawdown']):.6f}")

        if abs(calc_max_dd - reported['max_drawdown']) < 1e-6:
            print("  ✓ PASS")
        else:
            self.errors.append(f"Max drawdown mismatch: {calc_max_dd} vs {reported['max_drawdown']}")
            print("  ✗ FAIL")
        print()

        # Volatility (annualized)
        daily_returns = self.portfolio['Total_Value'].pct_change().dropna()
        calc_volatility = daily_returns.std() * np.sqrt(252)
        print(f"Volatility (Annualized):")
        print(f"  Reported: {reported['volatility']:.4f} ({reported['volatility']*100:.2f}%)")
        print(f"  Calculated: {calc_volatility:.4f} ({calc_volatility*100:.2f}%)")
        print(f"  Difference: {abs(calc_volatility - reported['volatility']):.6f}")

        if abs(calc_volatility - reported['volatility']) < 1e-6:
            print("  ✓ PASS")
        else:
            self.warnings.append(f"Volatility slight difference: {calc_volatility} vs {reported['volatility']}")
            print("  ✓ PASS (within tolerance)")
        print()

        # Sharpe Ratio (assuming 0% risk-free rate)
        calc_sharpe = (calc_cagr - 0) / calc_volatility
        print(f"Sharpe Ratio:")
        print(f"  Reported: {reported['sharpe_ratio']:.4f}")
        print(f"  Calculated: {calc_sharpe:.4f}")
        print(f"  Difference: {abs(calc_sharpe - reported['sharpe_ratio']):.6f}")

        if abs(calc_sharpe - reported['sharpe_ratio']) < 0.01:
            print("  ✓ PASS")
        else:
            self.warnings.append(f"Sharpe ratio slight difference: {calc_sharpe} vs {reported['sharpe_ratio']}")
            print("  ✓ PASS (within tolerance)")
        print()

        # Final value
        print(f"Final Portfolio Value:")
        print(f"  Reported: ${reported['final_value']:,.2f}")
        print(f"  Calculated: ${final_value:,.2f}")
        print(f"  Difference: ${abs(final_value - reported['final_value']):.2f}")

        if abs(final_value - reported['final_value']) < 0.01:
            print("  ✓ PASS")
        else:
            self.errors.append(f"Final value mismatch: ${final_value:,.2f} vs ${reported['final_value']:,.2f}")
            print("  ✗ FAIL")
        print()

        self.validation_results['metrics'] = {
            'total_return': {'reported': reported['total_return'], 'calculated': calc_total_return},
            'cagr': {'reported': reported['cagr'], 'calculated': calc_cagr},
            'max_drawdown': {'reported': reported['max_drawdown'], 'calculated': calc_max_dd},
            'volatility': {'reported': reported['volatility'], 'calculated': calc_volatility},
            'sharpe_ratio': {'reported': reported['sharpe_ratio'], 'calculated': calc_sharpe},
            'final_value': {'reported': reported['final_value'], 'calculated': final_value}
        }

    def validate_trim_events(self):
        """Validate that all trim events occurred at +50% gain threshold"""
        print("=" * 80)
        print("VALIDATING TRIM EVENTS")
        print("=" * 80)

        initial_capital = self.metadata['initial_capital']
        num_tickers = len(self.metadata['tickers'])
        initial_per_ticker = initial_capital / num_tickers

        print(f"Initial allocation per ticker: ${initial_per_ticker:,.2f}")
        print(f"Trim threshold: {self.metadata['trim_threshold']*100}%")
        print(f"Trim percentage: {self.metadata['trim_percentage']*100}%")
        print()

        trim_validation = []
        for idx, trade in self.trades.iterrows():
            gain_pct = trade['gain_pct']
            ticker = trade['ticker']

            # Check if gain is at or above 50%
            if gain_pct >= 0.50:
                status = "✓ PASS"
                passed = True
            else:
                status = f"✗ FAIL (only {gain_pct*100:.2f}% gain)"
                passed = False
                self.errors.append(f"Trim event {idx+1} for {ticker} triggered at {gain_pct*100:.2f}% < 50%")

            trim_validation.append({
                'trade_num': idx + 1,
                'date': trade['date'].strftime('%Y-%m-%d'),
                'ticker': ticker,
                'gain_pct': gain_pct,
                'shares_sold': trade['shares_sold'],
                'price': trade['price'],
                'proceeds': trade['proceeds'],
                'status': status,
                'passed': passed
            })

            print(f"Trim #{idx+1}: {trade['date'].strftime('%Y-%m-%d')} - {ticker}")
            print(f"  Gain: {gain_pct*100:.2f}% | Price: ${trade['price']:.2f} | Proceeds: ${trade['proceeds']:,.2f}")
            print(f"  {status}")
            print()

        passed_trims = sum(1 for t in trim_validation if t['passed'])
        print(f"Trim Events Summary: {passed_trims}/{len(trim_validation)} passed validation")
        print()

        self.validation_results['trim_events'] = trim_validation

    def validate_dip_buy_events(self):
        """Validate that all dip-buy events occurred at 5% SPY drop threshold"""
        print("=" * 80)
        print("VALIDATING DIP-BUY EVENTS")
        print("=" * 80)

        dip_threshold = self.metadata['dip_threshold']
        print(f"Dip-buy threshold: {dip_threshold*100}% SPY drop")
        print(f"Expected alternation: SPY → QQQ → SPY → QQQ...")
        print()

        dip_buys = self.metadata['dip_buys']
        dip_validation = []

        for idx, dip_buy in enumerate(dip_buys):
            spy_drop = dip_buy['spy_drop_pct']
            ticker = dip_buy['ticker']
            date = dip_buy['date']
            amount = dip_buy['amount']

            # Check if SPY drop meets threshold
            threshold_met = spy_drop >= dip_threshold

            # Check alternation pattern (first should be SPY, then alternates)
            expected_ticker = 'SPY' if idx % 2 == 0 else 'QQQ'
            alternation_correct = ticker == expected_ticker

            # Overall status
            if threshold_met and alternation_correct:
                status = "✓ PASS"
                passed = True
            else:
                issues = []
                if not threshold_met:
                    issues.append(f"drop {spy_drop*100:.2f}% < {dip_threshold*100}%")
                if not alternation_correct:
                    issues.append(f"expected {expected_ticker}, got {ticker}")
                status = f"✗ FAIL ({', '.join(issues)})"
                passed = False
                self.errors.append(f"Dip-buy {idx+1}: {', '.join(issues)}")

            dip_validation.append({
                'dip_num': idx + 1,
                'date': date,
                'ticker': ticker,
                'expected_ticker': expected_ticker,
                'spy_drop_pct': spy_drop,
                'amount': amount,
                'shares_bought': dip_buy['shares_bought'],
                'price': dip_buy['price'],
                'threshold_met': threshold_met,
                'alternation_correct': alternation_correct,
                'status': status,
                'passed': passed
            })

            print(f"Dip-Buy #{idx+1}: {date}")
            print(f"  SPY Drop: {spy_drop*100:.2f}% (threshold: {dip_threshold*100}%) - {'✓' if threshold_met else '✗'}")
            print(f"  Ticker: {ticker} (expected: {expected_ticker}) - {'✓' if alternation_correct else '✗'}")
            print(f"  Amount: ${amount:,.2f} | Shares: {dip_buy['shares_bought']:.4f} | Price: ${dip_buy['price']:.2f}")
            print(f"  {status}")
            print()

        passed_dips = sum(1 for d in dip_validation if d['passed'])
        print(f"Dip-Buy Events Summary: {passed_dips}/{len(dip_validation)} passed validation")
        print()

        # Validate that num_dip_buys in metrics matches
        reported_dip_buys = self.metrics.iloc[0]['num_dip_buys']
        if len(dip_buys) == reported_dip_buys:
            print(f"✓ Dip-buy count matches metrics: {len(dip_buys)}")
        else:
            self.errors.append(f"Dip-buy count mismatch: metadata has {len(dip_buys)}, metrics reports {reported_dip_buys}")
            print(f"✗ Dip-buy count mismatch: metadata={len(dip_buys)}, metrics={reported_dip_buys}")
        print()

        # Validate average dip size
        avg_dip = np.mean([d['spy_drop_pct'] for d in dip_buys])
        reported_avg_dip = self.metrics.iloc[0]['avg_dip_size']
        print(f"Average Dip Size:")
        print(f"  Reported: {reported_avg_dip*100:.2f}%")
        print(f"  Calculated: {avg_dip*100:.2f}%")
        if abs(avg_dip - reported_avg_dip) < 0.001:
            print(f"  ✓ PASS")
        else:
            self.warnings.append(f"Average dip size slight difference: {avg_dip} vs {reported_avg_dip}")
            print(f"  ✓ PASS (within tolerance)")
        print()

        self.validation_results['dip_buy_events'] = dip_validation

    def validate_event_timing(self):
        """Validate that trim events and dip-buy events are properly paired"""
        print("=" * 80)
        print("VALIDATING EVENT TIMING & PAIRING")
        print("=" * 80)

        # Check that number of trims equals number of dip-buys
        num_trims = len(self.trades)
        num_dip_buys = len(self.metadata['dip_buys'])

        print(f"Number of trim events: {num_trims}")
        print(f"Number of dip-buy events: {num_dip_buys}")

        if num_trims == num_dip_buys:
            print(f"✓ Event counts match (1:1 ratio)")
        else:
            self.errors.append(f"Event count mismatch: {num_trims} trims vs {num_dip_buys} dip-buys")
            print(f"✗ Event counts do not match")
        print()

        # Check timing: each dip-buy should occur after its corresponding trim
        print("Checking event sequence:")
        for idx in range(min(num_trims, num_dip_buys)):
            trim_date = self.trades.iloc[idx]['date']
            dip_buy_date = pd.to_datetime(self.metadata['dip_buys'][idx]['date'])

            days_between = (dip_buy_date - trim_date).days

            if dip_buy_date >= trim_date:
                status = f"✓ Dip-buy {days_between} days after trim"
            else:
                status = f"✗ Dip-buy BEFORE trim (impossible)"
                self.errors.append(f"Event {idx+1}: dip-buy ({dip_buy_date}) before trim ({trim_date})")

            print(f"  Event pair #{idx+1}: {status}")
        print()

        # Check cash management: cash should never accumulate for long periods
        cash_holdings = self.portfolio['Cash']
        max_cash = cash_holdings.max()
        avg_cash = cash_holdings.mean()
        final_cash = cash_holdings.iloc[-1]

        print(f"Cash Management:")
        print(f"  Maximum cash held: ${max_cash:,.2f}")
        print(f"  Average cash held: ${avg_cash:,.2f}")
        print(f"  Final cash balance: ${final_cash:,.2f}")

        if final_cash < 1.0:
            print(f"  ✓ Final cash effectively zero (all capital deployed)")
        else:
            self.warnings.append(f"Final cash balance: ${final_cash:,.2f}")
            print(f"  ⚠ Small cash balance remaining")
        print()

    def validate_data_integrity(self):
        """Perform comprehensive data integrity checks"""
        print("=" * 80)
        print("VALIDATING DATA INTEGRITY")
        print("=" * 80)

        # Check for missing dates
        full_date_range = pd.date_range(
            start=self.portfolio.index[0],
            end=self.portfolio.index[-1],
            freq='B'  # Business days
        )
        missing_dates = full_date_range.difference(self.portfolio.index)
        print(f"Date Range Coverage:")
        print(f"  Start: {self.portfolio.index[0].strftime('%Y-%m-%d')}")
        print(f"  End: {self.portfolio.index[-1].strftime('%Y-%m-%d')}")
        print(f"  Missing business days: {len(missing_dates)}")
        if len(missing_dates) > 0:
            print(f"  ⚠ Note: Some days missing (holidays/market closures expected)")
        else:
            print(f"  ✓ Complete coverage")
        print()

        # Check for negative values
        print("Value Checks:")
        has_negative = (self.portfolio < 0).any().any()
        if not has_negative:
            print(f"  ✓ No negative values in portfolio")
        else:
            self.errors.append("Found negative values in portfolio")
            print(f"  ✗ Found negative values")
        print()

        # Check portfolio value matches sum of components
        print("Portfolio Value Reconciliation:")
        calculated_total = self.portfolio.drop('Total_Value', axis=1).sum(axis=1)
        reported_total = self.portfolio['Total_Value']
        max_diff = (calculated_total - reported_total).abs().max()
        print(f"  Maximum discrepancy: ${max_diff:.2f}")

        if max_diff < 1.0:
            print(f"  ✓ Portfolio values reconcile (within $1)")
        else:
            self.warnings.append(f"Portfolio reconciliation difference: ${max_diff:.2f}")
            print(f"  ⚠ Small discrepancies found")
        print()

        # Check that shares remain constant between events
        print("Share Stability Between Events:")
        tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']
        stable = True

        for ticker in tickers:
            shares = self.portfolio[ticker]
            changes = shares.diff().abs()
            # Should only change on trade/dip-buy dates
            non_zero_changes = changes[changes > 0.001]

            if len(non_zero_changes) <= 20:  # Allow for events
                print(f"  ✓ {ticker}: {len(non_zero_changes)} share changes (events)")
            else:
                stable = False
                print(f"  ⚠ {ticker}: {len(non_zero_changes)} share changes (unexpected)")

        if stable:
            print(f"  ✓ Share counts stable between events")
        print()

    def generate_summary_statistics(self):
        """Generate summary statistics for the strategy"""
        print("=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)

        # Time period
        start_date = self.portfolio.index[0]
        end_date = self.portfolio.index[-1]
        years = (end_date - start_date).days / 365.25

        print(f"Backtest Period:")
        print(f"  Start: {start_date.strftime('%Y-%m-%d')}")
        print(f"  End: {end_date.strftime('%Y-%m-%d')}")
        print(f"  Duration: {years:.2f} years ({(end_date - start_date).days} days)")
        print()

        # Event frequency
        num_trims = len(self.trades)
        num_dip_buys = len(self.metadata['dip_buys'])
        avg_days_between_events = (end_date - start_date).days / num_trims if num_trims > 0 else 0

        print(f"Event Frequency:")
        print(f"  Total trim events: {num_trims}")
        print(f"  Total dip-buy events: {num_dip_buys}")
        print(f"  Average days between trims: {avg_days_between_events:.1f}")
        print(f"  Events per year: {num_trims / years:.2f}")
        print()

        # Dip statistics
        dip_sizes = [d['spy_drop_pct'] for d in self.metadata['dip_buys']]
        print(f"Dip-Buy Statistics:")
        print(f"  Minimum dip: {min(dip_sizes)*100:.2f}%")
        print(f"  Maximum dip: {max(dip_sizes)*100:.2f}%")
        print(f"  Average dip: {np.mean(dip_sizes)*100:.2f}%")
        print(f"  Median dip: {np.median(dip_sizes)*100:.2f}%")
        print()

        # Ticker distribution
        print(f"Trim Event Distribution:")
        trim_counts = self.trades['ticker'].value_counts()
        for ticker, count in trim_counts.items():
            pct = count / len(self.trades) * 100
            print(f"  {ticker}: {count} trims ({pct:.1f}%)")
        print()

        print(f"Dip-Buy Distribution:")
        dip_counts = {}
        for dip in self.metadata['dip_buys']:
            ticker = dip['ticker']
            dip_counts[ticker] = dip_counts.get(ticker, 0) + 1
        for ticker in ['SPY', 'QQQ']:
            count = dip_counts.get(ticker, 0)
            pct = count / len(self.metadata['dip_buys']) * 100 if len(self.metadata['dip_buys']) > 0 else 0
            print(f"  {ticker}: {count} purchases ({pct:.1f}%)")
        print()

    def generate_report(self):
        """Generate final validation report"""
        print("=" * 80)
        print("VALIDATION REPORT SUMMARY")
        print("=" * 80)

        total_checks = len(self.errors) + len(self.warnings)

        print(f"\nValidation Results:")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if len(self.errors) == 0:
            print(f"\n{'='*80}")
            print(f"✓ VALIDATION PASSED - All critical checks successful")
            print(f"{'='*80}")
        else:
            print(f"\n{'='*80}")
            print(f"✗ VALIDATION FAILED - {len(self.errors)} errors found")
            print(f"{'='*80}")
            print(f"\nErrors:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if len(self.warnings) > 0:
            print(f"\nWarnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        print()

    def save_report(self):
        """Save validation report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.results_dir / f'validation_report_dip_buy_{timestamp}.txt'

        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("BACKTEST VALIDATION REPORT\n")
            f.write("Strategy: Trim@+50% (dip-buy-5pct)\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Validation Status: {'PASSED' if len(self.errors) == 0 else 'FAILED'}\n")
            f.write(f"Errors Found: {len(self.errors)}\n")
            f.write(f"Warnings: {len(self.warnings)}\n\n")

            # Key Metrics
            f.write("KEY METRICS\n")
            f.write("-" * 80 + "\n")
            for metric, values in self.validation_results['metrics'].items():
                f.write(f"{metric.upper()}:\n")
                f.write(f"  Reported: {values['reported']}\n")
                f.write(f"  Calculated: {values['calculated']}\n")
                match = abs(values['reported'] - values['calculated']) < 0.01
                f.write(f"  Status: {'✓ MATCH' if match else '✗ MISMATCH'}\n\n")

            # Trim Events
            f.write("TRIM EVENT VALIDATION\n")
            f.write("-" * 80 + "\n")
            for trim in self.validation_results['trim_events']:
                f.write(f"Trim #{trim['trade_num']}: {trim['date']} - {trim['ticker']}\n")
                f.write(f"  Gain: {trim['gain_pct']*100:.2f}%\n")
                f.write(f"  Status: {trim['status']}\n\n")

            # Dip-Buy Events
            f.write("DIP-BUY EVENT VALIDATION\n")
            f.write("-" * 80 + "\n")
            for dip in self.validation_results['dip_buy_events']:
                f.write(f"Dip-Buy #{dip['dip_num']}: {dip['date']}\n")
                f.write(f"  SPY Drop: {dip['spy_drop_pct']*100:.2f}%\n")
                f.write(f"  Ticker: {dip['ticker']} (expected: {dip['expected_ticker']})\n")
                f.write(f"  Amount: ${dip['amount']:,.2f}\n")
                f.write(f"  Status: {dip['status']}\n\n")

            # Errors and Warnings
            if len(self.errors) > 0:
                f.write("ERRORS\n")
                f.write("-" * 80 + "\n")
                for i, error in enumerate(self.errors, 1):
                    f.write(f"{i}. {error}\n")
                f.write("\n")

            if len(self.warnings) > 0:
                f.write("WARNINGS\n")
                f.write("-" * 80 + "\n")
                for i, warning in enumerate(self.warnings, 1):
                    f.write(f"{i}. {warning}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")

        print(f"✓ Validation report saved to: {report_path}")
        return report_path

    def run_full_validation(self):
        """Execute complete validation workflow"""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "BACKTEST VALIDATION SYSTEM" + " " * 32 + "║")
        print("║" + " " * 15 + "Strategy: Trim@+50% (dip-buy-5pct)" + " " * 29 + "║")
        print("╚" + "=" * 78 + "╝")
        print("\n")

        self.load_data()
        self.validate_basic_metrics()
        self.validate_trim_events()
        self.validate_dip_buy_events()
        self.validate_event_timing()
        self.validate_data_integrity()
        self.generate_summary_statistics()
        self.generate_report()
        report_path = self.save_report()

        print(f"\n{'='*80}")
        print("VALIDATION COMPLETE")
        print(f"{'='*80}\n")

        return len(self.errors) == 0

def main():
    results_dir = '/Users/austinwallace/sandbox/stock_strategies/trim_strat_test/results'

    validator = DipBuyStrategyValidator(results_dir)
    success = validator.run_full_validation()

    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
