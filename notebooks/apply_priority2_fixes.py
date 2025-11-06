#!/usr/bin/env python
"""
Apply all Priority 2 fixes from fact-checker to COMPREHENSIVE_BACKTEST_REPORT.ipynb
"""

import json

# Read the notebook
with open('COMPREHENSIVE_BACKTEST_REPORT.ipynb', 'r') as f:
    notebook = json.load(f)

print("=" * 80)
print("APPLYING PRIORITY 2 FIXES TO COMPREHENSIVE_BACKTEST_REPORT.ipynb")
print("=" * 80)

fixes_applied = []

# ============================================================================
# FIX 5: Clarify parameter choices
# ============================================================================
print("\n[FIX 5] Adding parameter choice disclaimers...")

for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])

        # Find methodology section with threshold descriptions
        if '#### 1. Threshold-Based' in source and '**Parameter Note:**' not in source:
            # Add disclaimer after threshold descriptions
            param_note = """

**Parameter Note:** The thresholds (+50%, +100%, +150%) are **arbitrary round numbers** chosen for clarity and interpretability, not derived from optimization or theoretical models. Similarly, the 20% trim size is illustrative. The "optimal" parameters (if they exist) would vary by investor risk tolerance, tax situation, and market regime.

"""
            # Insert after the threshold list
            lines = source.split('\n')
            insert_idx = None
            for j, line in enumerate(lines):
                if '**+150%**: Conservative, 10 trims' in line:
                    insert_idx = j + 1
                    break

            if insert_idx:
                lines.insert(insert_idx + 1, param_note)
                source = '\n'.join(lines)
                cell['source'] = source.split('\n')
                if not cell['source'][-1]:
                    cell['source'] = cell['source'][:-1]
                fixes_applied.append("✓ Added threshold parameter disclaimer")
                print("  ✓ Added threshold parameter note")

        # Find volatility strategy section
        if '#### 3. Volatility-Based' in source and 'illustrative thresholds' not in source:
            old_source = source
            # Add disclaimer about volatility thresholds
            source = source.replace(
                '**Protection Mechanisms**:',
                '**Thresholds Tested**: 1.5×, 2.0×, 2.5× are **illustrative multipliers**, not optimized. These values were selected pragmatically after observing that 1.5× triggered too frequently (325 trims) while 2.5× hit a "sweet spot" (~47 trims).\n\n**Protection Mechanisms**:'
            )

            # Add note about cooldown/hysteresis
            source = source.replace(
                '- **Hysteresis**: Entry at 2.5×, exit at 2.25× (prevents whipsaw)',
                '- **Hysteresis**: Entry at 2.5×, exit at 2.25× (prevents whipsaw)\n\n**Note on Protection Values**: The 10-day cooldown and 0.9× hysteresis are **pragmatic choices**, not scientifically optimized. They prevent overtrading but could be fine-tuned. Consider them reasonable starting points, not universal constants.'
            )

            if source != old_source:
                cell['source'] = source.split('\n')
                if not cell['source'][-1]:
                    cell['source'] = cell['source'][:-1]
                fixes_applied.append("✓ Added volatility parameter disclaimers")
                print("  ✓ Added volatility parameter notes")

# ============================================================================
# FIX 6: Reconcile sensitivity analysis
# ============================================================================
print("\n[FIX 6] Reconciling sensitivity analysis...")

for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])

        # Find sensitivity analysis section
        if '**Key Finding**: Smaller trim sizes (10-15%)' in source and 'Why 20% is used' not in source:
            # Add reconciliation note
            reconciliation = """

**Reconciliation Note:** The sensitivity analysis suggests 10-15% trim sizes outperform the 20% used in the main backtest. Why didn't we re-run with 10%?

1. **Discovered late**: Sensitivity analysis was performed after completing the 42-strategy backtest
2. **Time cost**: Re-running 42 strategies × 2,477 days with new trim size would take significant computation time
3. **Future work**: Testing 10% trim size across all strategies is identified as immediate next step

**Practical implication**: If you implement these strategies, consider testing 10-15% trim sizes. The main backtest results with 20% trims are conservative - actual optimal performance may be 1-2% CAGR higher.
"""
            source += reconciliation
            cell['source'] = source.split('\n')
            if not cell['source'][-1]:
                cell['source'] = cell['source'][:-1]
            fixes_applied.append("✓ Added sensitivity reconciliation note")
            print("  ✓ Added sensitivity analysis reconciliation")

# ============================================================================
# FIX 7: Note about cost/tax validation (not running actual backtest)
# ============================================================================
print("\n[FIX 7] Adding cost/tax validation note...")

for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])

        # Find cost/tax modeling section
        if '## 2.5 Cost & Tax Modeling (NEW)' in source and 'Projected Impact' not in source:
            # Find expected impact section and clarify these are projections
            old_source = source
            source = source.replace(
                '**Expected impact with realistic costs (0.1% + 20% tax)**:',
                '**Projected Impact with Realistic Costs (0.1% + 20% tax)**:\n\n*Note: These are PROJECTIONS based on trade frequency, not from running the backtest with costs enabled. To test actual impact, set the toggles and re-run the backtest.*'
            )

            if source != old_source:
                cell['source'] = source.split('\n')
                if not cell['source'][-1]:
                    cell['source'] = cell['source'][:-1]
                fixes_applied.append("✓ Clarified cost/tax projections")
                print("  ✓ Clarified cost/tax are projections")

# ============================================================================
# FIX 8: Fix 60/40 terminology confusion
# ============================================================================
print("\n[FIX 8] Fixing 60/40 terminology...")

replacements_made = 0
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])
        old_source = source

        # Replace ambiguous "60/40 portfolio" with clear "60/40 index/stock split"
        # But preserve "60/40 SPY+AGG" references (that's the traditional meaning)
        source = source.replace('60/40 Portfolio', '60/40 Index/Stock Portfolio')
        source = source.replace('Our 60/40 Portfolio', 'Our 60/40 Index/Stock Portfolio')
        source = source.replace('60/40 split', '60/40 index/stock split')

        # Add clarification in first mention
        if 'Portfolio**: 60% Index Funds' in source and '100% equity' not in source:
            source = source.replace(
                'Portfolio**: 60% Index Funds (SPY, QQQ, VOO) + 40% Individual Stocks',
                'Portfolio**: 60% Index Funds (SPY, QQQ, VOO) + 40% Individual Stocks *(Note: 100% equity allocation, not traditional 60/40 stocks/bonds)*'
            )

        if source != old_source:
            cell['source'] = source.split('\n')
            if not cell['source'][-1]:
                cell['source'] = cell['source'][:-1]
            replacements_made += 1

if replacements_made > 0:
    fixes_applied.append(f"✓ Fixed 60/40 terminology in {replacements_made} cells")
    print(f"  ✓ Fixed 60/40 terminology in {replacements_made} cells")

# Add explicit clarification in Benchmarks section
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])

        if 'Note: 60/40 SPY+AGG benchmark not calculated' in source and 'TERMINOLOGY' not in source:
            clarification = """

**TERMINOLOGY CLARIFICATION**:
- **Our "60/40" portfolio** = 60% index funds + 40% individual stocks (100% equity)
- **Traditional "60/40" benchmark** = 60% stocks (SPY) + 40% bonds (AGG)

We use "60/40" to mean index/stock split, not the traditional stock/bond allocation. To avoid confusion, we'll use "60/40 index/stock split" going forward.
"""
            source += clarification
            cell['source'] = source.split('\n')
            if not cell['source'][-1]:
                cell['source'] = cell['source'][:-1]
            fixes_applied.append("✓ Added terminology clarification in Benchmarks")
            print("  ✓ Added terminology clarification section")
            break

# ============================================================================
# Save updated notebook
# ============================================================================

with open('COMPREHENSIVE_BACKTEST_REPORT.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)

print("\n" + "=" * 80)
print("FIXES APPLIED SUMMARY")
print("=" * 80)
for fix in fixes_applied:
    print(fix)

print(f"\n✅ Successfully applied {len(fixes_applied)} Priority 2 fixes")
print("=" * 80)
