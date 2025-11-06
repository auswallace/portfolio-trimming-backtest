#!/usr/bin/env python
"""
Apply all 4 Priority 1 fixes from fact-checker to COMPREHENSIVE_BACKTEST_REPORT.ipynb
"""

import json
import re

# Read the notebook
with open('COMPREHENSIVE_BACKTEST_REPORT.ipynb', 'r') as f:
    notebook = json.load(f)

print("=" * 80)
print("APPLYING PRIORITY 1 FIXES TO COMPREHENSIVE_BACKTEST_REPORT.ipynb")
print("=" * 80)

fixes_applied = []

# ============================================================================
# FIX 1: Correct Rolling 3yr CAGR factual error
# ============================================================================
print("\n[FIX 1] Correcting rolling 3yr CAGR values...")

for cell in notebook['cells']:
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])

        # Fix Buy-and-Hold rolling 3yr CAGR mean (actual: 25.50%)
        if '23.17%' in source or '26.87%' in source:
            # Replace incorrect values with correct one
            old_source = source
            source = source.replace('23.17%', '25.50%')
            source = source.replace('26.87%', '25.50%')

            if source != old_source:
                cell['source'] = source.split('\n')
                if not cell['source'][-1]:  # Remove empty last element if exists
                    cell['source'] = cell['source'][:-1]
                fixes_applied.append("✓ Fixed rolling 3yr CAGR value (23.17%/26.87% → 25.50%)")
                print(f"  ✓ Fixed rolling 3yr CAGR in markdown cell")

# ============================================================================
# FIX 2: Resolve missing validation report reference
# ============================================================================
print("\n[FIX 2] Fixing validation report references...")

for cell in notebook['cells']:
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])

        if 'docs/validation/COMPREHENSIVE_VALIDATION_REPORT.md' in source:
            old_source = source
            # Replace with actual validation script reference
            source = source.replace(
                'docs/validation/COMPREHENSIVE_VALIDATION_REPORT.md',
                'src/validation/comprehensive_validation.py'
            )
            # Add disclaimer about validation
            if 'Validation script' in source and 'performed live' not in source:
                source = source.replace(
                    'Validation script: `src/validation/comprehensive_validation.py`',
                    'Validation script: `src/validation/comprehensive_validation.py` (validation performed live during development, see CLAUDE.md Session 5 for results)'
                )

            if source != old_source:
                cell['source'] = source.split('\n')
                if not cell['source'][-1]:
                    cell['source'] = cell['source'][:-1]
                fixes_applied.append("✓ Fixed validation report reference")
                print(f"  ✓ Updated validation report reference")

# ============================================================================
# FIX 3: Soften "realistic portfolio" assumptions
# ============================================================================
print("\n[FIX 3] Softening unjustified assumptions...")

replacements = [
    ('realistic portfolio', 'illustrative portfolio'),
    ('typical investor', 'example investor scenario'),
    ('Represents typical investor', 'Represents an example investor'),
    ('More realistic than', 'More illustrative than'),
]

cells_updated = 0
for cell in notebook['cells']:
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])
        old_source = source

        for old, new in replacements:
            source = source.replace(old, new)

        if source != old_source:
            cell['source'] = source.split('\n')
            if not cell['source'][-1]:
                cell['source'] = cell['source'][:-1]
            cells_updated += 1

if cells_updated > 0:
    fixes_applied.append(f"✓ Softened assumptions in {cells_updated} cells")
    print(f"  ✓ Updated language in {cells_updated} cells")

# Add disclaimer after portfolio table (Section 1)
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])

        # Find portfolio table section
        if '| TSLA | 10% | Tesla |' in source and '**Important Caveats**' not in source:
            # Add disclaimer after table
            disclaimer = """

**Important Caveats:**
- This 60/40 index/stock split is an **illustrative allocation**, not based on survey data of actual retail portfolios
- Ticker selection represents **plausible holdings** for a 2015 investor, not validated against typical portfolios
- SPY + VOO redundancy (40% total S&P 500 exposure) acknowledged but not corrected for simplicity
- Results are specific to these holdings and may not generalize to other portfolio compositions

"""
            source += disclaimer
            cell['source'] = source.split('\n')
            if not cell['source'][-1]:
                cell['source'] = cell['source'][:-1]
            fixes_applied.append("✓ Added portfolio caveats disclaimer")
            print(f"  ✓ Added Important Caveats section")
            break

# ============================================================================
# FIX 4: Add statistical significance discussion
# ============================================================================
print("\n[FIX 4] Adding statistical significance discussion...")

# Find Section 5 (Discussion) and add new subsection after "Why Volatility-2.5× Works"
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source'])

        # Find the right section (after "Why Volatility-2.5× Works" subsection)
        if '### Why Volatility-2.5× Works' in source and '### Statistical Significance' not in source:
            # Find the end of this subsection (next ### or end of cell)
            lines = source.split('\n')
            insert_index = len(lines)
            for j, line in enumerate(lines):
                if j > 0 and line.startswith('### ') and 'Why Volatility' not in line:
                    insert_index = j
                    break

            # Insert statistical significance section
            sig_section = """

### Statistical Significance Considerations

**Bootstrap CI Overlap Analysis**:
- Buy-and-Hold 95% CI: 3.58% to 43.72% CAGR
- Volatility-2.5× (pro-rata) 95% CI: 3.74% to 58.92% CAGR
- **Significant overlap**: Both strategies' CIs span similar ranges

**Interpretation**:
- Observed outperformance (26.98% vs 21.69%) occurred in **this specific sample** (2015-2024)
- Wide CIs reflect high uncertainty in outcome estimates
- Without formal hypothesis testing (t-tests, p-values), we cannot conclude outperformance is statistically significant at conventional levels (p<0.05)
- Recommendation: Interpret results as "outperformed in this sample period" not "will outperform in future"

**Practical Takeaway**: The observed 52% advantage may partially reflect luck/sample variation rather than purely strategy superiority. Longer backtests or out-of-sample testing recommended for higher confidence.

"""
            lines.insert(insert_index, sig_section)
            cell['source'] = '\n'.join(lines).split('\n')
            if not cell['source'][-1]:
                cell['source'] = cell['source'][:-1]
            fixes_applied.append("✓ Added statistical significance discussion")
            print(f"  ✓ Added Statistical Significance Considerations subsection")
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

print(f"\n✅ Successfully applied {len(fixes_applied)} fixes to COMPREHENSIVE_BACKTEST_REPORT.ipynb")
print("=" * 80)
