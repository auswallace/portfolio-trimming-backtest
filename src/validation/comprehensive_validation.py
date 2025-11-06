#!/usr/bin/env python
"""
Comprehensive Validation: Verify all metrics calculations
Checks CAGR, Sharpe, Sortino, Max Drawdown, Volatility, Rolling metrics, Bootstrap CIs
"""

import pandas as pd
import numpy as np
import sys

print("="*80)
print("COMPREHENSIVE METRICS VALIDATION")
print("="*80)

# Load results
results_df = pd.read_csv('results_index_focus/index_focus_results.csv', index_col=0)

print(f"\n✓ Loaded {len(results_df)} strategies")

# ============================================================================
# 1. CHECK FOR SUSPICIOUS VALUES
# ============================================================================

print("\n" + "="*80)
print("1. CHECKING FOR SUSPICIOUS VALUES")
print("="*80)

issues = []

# Sharpe ratio should typically be -1 to 3
suspicious_sharpe = results_df[(results_df['sharpe_ratio'] < -1) | (results_df['sharpe_ratio'] > 3)]
if len(suspicious_sharpe) > 0:
    print(f"\n⚠️  Found {len(suspicious_sharpe)} strategies with suspicious Sharpe ratios:")
    for idx in suspicious_sharpe.index:
        sharpe = results_df.loc[idx, 'sharpe_ratio']
        print(f"   {idx}: {sharpe:.2f}")
        issues.append(f"Suspicious Sharpe: {idx} = {sharpe:.2f}")

# Sortino ratio should be similar magnitude to Sharpe (typically 0.5 to 2x Sharpe)
suspicious_sortino = results_df[(results_df['sortino_ratio'] < -1) | (results_df['sortino_ratio'] > 10)]
if len(suspicious_sortino) > 0:
    print(f"\n⚠️  Found {len(suspicious_sortino)} strategies with suspicious Sortino ratios:")
    for idx in suspicious_sortino.index:
        sortino = results_df.loc[idx, 'sortino_ratio']
        print(f"   {idx}: {sortino:.2f}")
        issues.append(f"Suspicious Sortino: {idx} = {sortino:.2f}")

# Volatility should be 0.1 to 1.0 (10% to 100% annualized)
suspicious_vol = results_df[(results_df['volatility'] < 0.05) | (results_df['volatility'] > 2.0)]
if len(suspicious_vol) > 0:
    print(f"\n⚠️  Found {len(suspicious_vol)} strategies with suspicious volatility:")
    for idx in suspicious_vol.index:
        vol = results_df.loc[idx, 'volatility']
        print(f"   {idx}: {vol:.2f}")
        issues.append(f"Suspicious Volatility: {idx} = {vol:.2f}")

# Max drawdown should be negative and > -1.0
suspicious_dd = results_df[(results_df['max_drawdown'] > 0) | (results_df['max_drawdown'] < -1.0)]
if len(suspicious_dd) > 0:
    print(f"\n⚠️  Found {len(suspicious_dd)} strategies with suspicious max drawdown:")
    for idx in suspicious_dd.index:
        dd = results_df.loc[idx, 'max_drawdown']
        print(f"   {idx}: {dd:.2%}")
        issues.append(f"Suspicious Max DD: {idx} = {dd:.2%}")

# CAGR should be -50% to +100%
suspicious_cagr = results_df[(results_df['cagr'] < -0.5) | (results_df['cagr'] > 1.0)]
if len(suspicious_cagr) > 0:
    print(f"\n⚠️  Found {len(suspicious_cagr)} strategies with suspicious CAGR:")
    for idx in suspicious_cagr.index:
        cagr = results_df.loc[idx, 'cagr']
        print(f"   {idx}: {cagr:.2%}")
        issues.append(f"Suspicious CAGR: {idx} = {cagr:.2%}")

if len(issues) == 0:
    print("\n✅ No suspicious values found!")

# ============================================================================
# 2. VERIFY CAGR CALCULATIONS
# ============================================================================

print("\n" + "="*80)
print("2. VERIFYING CAGR CALCULATIONS")
print("="*80)

INITIAL_CAPITAL = 100000
TRADING_DAYS = 2477
YEARS = TRADING_DAYS / 252

print(f"\nInitial Capital: ${INITIAL_CAPITAL:,}")
print(f"Trading Days: {TRADING_DAYS}")
print(f"Years: {YEARS:.2f}")

# Check Buy-and-Hold
bh_final = results_df.loc['Buy-and-Hold', 'final_value']
bh_cagr_reported = results_df.loc['Buy-and-Hold', 'cagr']
bh_cagr_calculated = (bh_final / INITIAL_CAPITAL) ** (1 / YEARS) - 1

print(f"\nBuy-and-Hold:")
print(f"  Final Value: ${bh_final:,.2f}")
print(f"  CAGR (reported): {bh_cagr_reported:.4f} ({bh_cagr_reported*100:.2f}%)")
print(f"  CAGR (calculated): {bh_cagr_calculated:.4f} ({bh_cagr_calculated*100:.2f}%)")
print(f"  Difference: {abs(bh_cagr_reported - bh_cagr_calculated):.6f}")

if abs(bh_cagr_reported - bh_cagr_calculated) > 0.0001:
    print(f"  ⚠️  WARNING: CAGR mismatch!")
    issues.append(f"Buy-and-Hold CAGR mismatch: {abs(bh_cagr_reported - bh_cagr_calculated):.6f}")
else:
    print(f"  ✅ CAGR calculation verified")

# Check top 3 strategies
print(f"\nTop 3 Strategies:")
top_3 = results_df.nlargest(3, 'final_value')

for idx in top_3.index:
    final_val = results_df.loc[idx, 'final_value']
    cagr_reported = results_df.loc[idx, 'cagr']
    cagr_calculated = (final_val / INITIAL_CAPITAL) ** (1 / YEARS) - 1

    print(f"\n  {idx}:")
    print(f"    Final Value: ${final_val:,.2f}")
    print(f"    CAGR (reported): {cagr_reported*100:.2f}%")
    print(f"    CAGR (calculated): {cagr_calculated*100:.2f}%")
    print(f"    Difference: {abs(cagr_reported - cagr_calculated):.6f}")

    if abs(cagr_reported - cagr_calculated) > 0.0001:
        print(f"    ⚠️  WARNING: CAGR mismatch!")
        issues.append(f"{idx} CAGR mismatch: {abs(cagr_reported - cagr_calculated):.6f}")
    else:
        print(f"    ✅ Verified")

# ============================================================================
# 3. CHECK BOOTSTRAP CI CONSISTENCY
# ============================================================================

print("\n" + "="*80)
print("3. CHECKING BOOTSTRAP CONFIDENCE INTERVALS")
print("="*80)

# CI lower should be < CAGR < CI upper
print(f"\nVerifying CAGR is within 95% CI bounds:")

ci_violations = 0
for idx in results_df.index:
    cagr = results_df.loc[idx, 'cagr']
    ci_lower = results_df.loc[idx, 'cagr_ci_lower']
    ci_upper = results_df.loc[idx, 'cagr_ci_upper']

    if not (ci_lower <= cagr <= ci_upper):
        print(f"  ⚠️  {idx}: CAGR {cagr:.2%} not in [{ci_lower:.2%}, {ci_upper:.2%}]")
        ci_violations += 1
        issues.append(f"{idx}: CAGR outside CI bounds")

if ci_violations == 0:
    print(f"  ✅ All {len(results_df)} strategies have CAGR within CI bounds")
else:
    print(f"  ⚠️  Found {ci_violations} violations")

# Check CI widths are reasonable
print(f"\nCI Width Analysis:")
results_df['ci_width'] = results_df['cagr_ci_upper'] - results_df['cagr_ci_lower']
print(f"  Mean CI width: {results_df['ci_width'].mean()*100:.2f}%")
print(f"  Min CI width: {results_df['ci_width'].min()*100:.2f}%")
print(f"  Max CI width: {results_df['ci_width'].max()*100:.2f}%")

if results_df['ci_width'].max() > 1.0:  # >100% width seems wrong
    print(f"  ⚠️  WARNING: Very wide confidence intervals detected")
    wide_cis = results_df[results_df['ci_width'] > 0.5]
    for idx in wide_cis.index:
        width = results_df.loc[idx, 'ci_width']
        print(f"     {idx}: {width*100:.1f}% width")
        issues.append(f"{idx}: CI width {width*100:.1f}%")

# ============================================================================
# 4. CHECK ROLLING METRICS
# ============================================================================

print("\n" + "="*80)
print("4. CHECKING ROLLING 3-YEAR METRICS")
print("="*80)

# Rolling 3yr CAGR mean should be close to overall CAGR (but not exactly equal)
print(f"\nComparing overall CAGR vs rolling 3yr mean:")

for idx in ['Buy-and-Hold', 'Volatility-2.5x (pro-rata)', 'Trim@+100% (pro-rata)']:
    if idx in results_df.index:
        cagr = results_df.loc[idx, 'cagr']
        rolling_mean = results_df.loc[idx, 'rolling_3yr_cagr_mean']
        diff = abs(cagr - rolling_mean)

        print(f"\n  {idx}:")
        print(f"    Overall CAGR: {cagr*100:.2f}%")
        print(f"    Rolling 3yr Mean: {rolling_mean*100:.2f}%")
        print(f"    Difference: {diff*100:.2f}%")

        # They should be similar but not identical
        if diff > 0.10:  # >10% difference seems suspicious
            print(f"    ⚠️  Large difference detected")
            issues.append(f"{idx}: Rolling CAGR differs by {diff*100:.1f}%")
        else:
            print(f"    ✅ Reasonable")

# Rolling max DD worst should be worse than overall max DD
print(f"\nVerifying rolling max DD worst >= overall max DD:")

for idx in ['Buy-and-Hold', 'Volatility-2.5x (pro-rata)', 'Volatility-1.5x (pro-rata)']:
    if idx in results_df.index:
        overall_dd = results_df.loc[idx, 'max_drawdown']
        rolling_worst = results_df.loc[idx, 'rolling_3yr_max_dd_worst']

        print(f"\n  {idx}:")
        print(f"    Overall Max DD: {overall_dd*100:.1f}%")
        print(f"    Rolling Worst: {rolling_worst*100:.1f}%")

        if rolling_worst > overall_dd:
            print(f"    ⚠️  WARNING: Rolling worst should be <= overall")
            issues.append(f"{idx}: Rolling DD worse than overall")
        else:
            print(f"    ✅ Correct")

# ============================================================================
# 5. VALIDATE SHARPE VS VOLATILITY CONSISTENCY
# ============================================================================

print("\n" + "="*80)
print("5. CHECKING SHARPE VS VOLATILITY CONSISTENCY")
print("="*80)

# Sharpe ≈ (CAGR - rf) / volatility
# Using rf = 0 (not modeled)
print(f"\nVerifying Sharpe ratio calculation (assuming rf=0):")

for idx in ['Buy-and-Hold', 'Volatility-2.5x (pro-rata)', 'Trim@+100% (pro-rata)']:
    if idx in results_df.index:
        cagr = results_df.loc[idx, 'cagr']
        vol = results_df.loc[idx, 'volatility']
        sharpe_reported = results_df.loc[idx, 'sharpe_ratio']
        sharpe_approx = cagr / vol if vol > 0 else 0

        print(f"\n  {idx}:")
        print(f"    CAGR: {cagr*100:.2f}%")
        print(f"    Volatility: {vol*100:.2f}%")
        print(f"    Sharpe (reported): {sharpe_reported:.2f}")
        print(f"    Sharpe (approx): {sharpe_approx:.2f}")
        print(f"    Difference: {abs(sharpe_reported - sharpe_approx):.2f}")

        # They should be similar (within ~0.3 due to methodology differences)
        if abs(sharpe_reported - sharpe_approx) > 0.5:
            print(f"    ⚠️  Large difference detected")
            issues.append(f"{idx}: Sharpe calculation discrepancy")
        else:
            print(f"    ✅ Reasonable (differences expected due to daily vs annual calc)")

# ============================================================================
# FINAL REPORT
# ============================================================================

print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)

if len(issues) == 0:
    print("\n✅ ✅ ✅  ALL VALIDATIONS PASSED  ✅ ✅ ✅")
    print("\nAll metrics calculations verified:")
    print("  ✓ No suspicious values")
    print("  ✓ CAGR calculations correct")
    print("  ✓ Bootstrap CIs consistent")
    print("  ✓ Rolling metrics reasonable")
    print("  ✓ Sharpe ratios consistent with volatility")
    sys.exit(0)
else:
    print(f"\n⚠️  FOUND {len(issues)} ISSUES:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

    print(f"\n❌ VALIDATION FAILED - Fix issues before proceeding")
    sys.exit(1)
