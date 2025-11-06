#!/usr/bin/env python
"""
Notebook Validation Script

Validates that all chart references in the notebook exist and can be loaded.
Also checks for author attribution correctness.

Author: Austin Wallace
Date: November 2024
"""

import json
import os
from pathlib import Path

print("="*80)
print("NOTEBOOK VALIDATION")
print("="*80)

# Load notebook
notebook_path = 'RESEARCH_REPORT_FINAL_CONDENSED.ipynb'
print(f"\nLoading notebook: {notebook_path}")

with open(notebook_path, 'r') as f:
    notebook = json.load(f)

print(f"  Loaded {len(notebook['cells'])} cells")

# Check 1: Author attribution
print("\n" + "-"*80)
print("CHECK 1: Author Attribution")
print("-"*80)

author_found = False
correct_author = False

for cell in notebook['cells']:
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'Author:' in source:
            author_found = True
            if 'Austin Wallace' in source:
                correct_author = True
                print("  PASS: Author correctly listed as Austin Wallace")
            elif 'Dick Capital' in source:
                print("  FAIL: Author still shows as Dick Capital")
            else:
                print(f"  WARNING: Found 'Author:' but unknown name")

if not author_found:
    print("  WARNING: No author attribution found")

# Check 2: Chart references
print("\n" + "-"*80)
print("CHECK 2: Chart File References")
print("-"*80)

chart_references = []
missing_charts = []
existing_charts = []

for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'Image(' in source and 'visualizations/' in source:
            # Extract image path
            import re
            matches = re.findall(r"Image\('([^']+)'\)", source)
            for match in matches:
                chart_references.append(match)

print(f"\nFound {len(chart_references)} chart references:")

for chart_path in chart_references:
    exists = os.path.exists(chart_path)
    size = os.path.getsize(chart_path) if exists else 0

    if exists:
        existing_charts.append(chart_path)
        print(f"  [FOUND] {chart_path} ({size:,} bytes)")
    else:
        missing_charts.append(chart_path)
        print(f"  [MISSING] {chart_path}")

# Check 3: List all visualization files
print("\n" + "-"*80)
print("CHECK 3: Available Visualization Files")
print("-"*80)

viz_dir = 'visualizations'
if os.path.exists(viz_dir):
    all_charts = sorted([f for f in os.listdir(viz_dir) if f.endswith('.png')])
    print(f"\nFound {len(all_charts)} PNG files in {viz_dir}/:")

    for chart in all_charts:
        full_path = os.path.join(viz_dir, chart)
        size = os.path.getsize(full_path)
        referenced = full_path in chart_references
        status = "[USED]" if referenced else "[UNUSED]"
        print(f"  {status} {chart} ({size:,} bytes)")
else:
    print(f"  ERROR: Directory {viz_dir}/ not found!")

# Check 4: Impressive visualizations
print("\n" + "-"*80)
print("CHECK 4: Impressive Visualization Files")
print("-"*80)

impressive_charts = [
    'impressive_performance_waterfall.png',
    'impressive_efficient_frontier.png',
    'impressive_drawdown_timeline.png',
    'impressive_performance_heatmap.png',
    'impressive_rolling_returns.png',
    'impressive_radar_chart.png',
    'impressive_cumulative_returns.png',
]

print(f"\nChecking {len(impressive_charts)} impressive charts:")

all_impressive_exist = True
for chart in impressive_charts:
    full_path = os.path.join(viz_dir, chart)
    exists = os.path.exists(full_path)
    size = os.path.getsize(full_path) if exists else 0
    referenced = full_path in chart_references

    if exists:
        status = "[EXISTS]"
        ref_status = "USED" if referenced else "NOT USED"
        print(f"  {status} {chart} - {ref_status} ({size:,} bytes)")
    else:
        status = "[MISSING]"
        all_impressive_exist = False
        print(f"  {status} {chart}")

# Summary
print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)

checks_passed = 0
total_checks = 4

if correct_author:
    print("  [PASS] Author attribution correct")
    checks_passed += 1
else:
    print("  [FAIL] Author attribution incorrect or missing")

if len(missing_charts) == 0:
    print(f"  [PASS] All {len(chart_references)} chart references valid")
    checks_passed += 1
else:
    print(f"  [FAIL] {len(missing_charts)} chart references broken")

if len(existing_charts) > 0:
    print(f"  [PASS] Found {len(existing_charts)} working charts")
    checks_passed += 1
else:
    print("  [FAIL] No working chart references found")

if all_impressive_exist:
    print(f"  [PASS] All {len(impressive_charts)} impressive charts exist")
    checks_passed += 1
else:
    print(f"  [FAIL] Some impressive charts missing")

print(f"\nOverall: {checks_passed}/{total_checks} checks passed")

if checks_passed == total_checks:
    print("\nRESULT: Notebook is ready for use!")
    exit(0)
else:
    print("\nRESULT: Notebook has issues that need fixing")
    exit(1)
