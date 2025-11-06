# 🚀 NEXT SESSION: Start Here

**Last Session**: UPDATE 3 complete, all work committed (commit `d8b25c8`)
**This Session**: Organizational cleanup (~45 minutes)

---

## ✅ WHAT'S DONE (Don't Touch)

- ✅ UPDATE 3: Cost/tax toggles implemented
- ✅ Comprehensive validation performed (all metrics accurate)
- ✅ Fact-checker review complete (9.5/10 quality)
- ✅ All Priority 1 & 2 fixes applied
- ✅ 6 chart insights added
- ✅ Notebook publication-ready (37 cells)
- ✅ **Everything committed to git**

---

## 🎯 TODAY'S WORK: File Organization

**Reference**: Read `ORGANIZATIONAL_CLEANUP_PLAN.md` for full details

**Quick Tasks** (execute in order):

### 1. Archive Temporary Scripts (~5 min)
```bash
mkdir -p scripts/archive
mv notebooks/apply_priority1_fixes.py scripts/archive/
mv notebooks/apply_priority2_fixes.py scripts/archive/
mv notebooks/add_chart_insights.py scripts/archive/
mv notebooks/complete_notebook.py scripts/archive/
mv notebooks/update_notebook_with_cost_tax.py scripts/archive/

cat > scripts/archive/README.md << 'EOF'
# Archived Scripts

One-time-use scripts from UPDATE 3 (November 2025). Used to apply fact-checker fixes and enhancements to COMPREHENSIVE_BACKTEST_REPORT.ipynb.

DO NOT RUN - preserved for reference only.

See docs/sessions/UPDATE_SESSION_SUMMARY.md for what changes were made.
EOF
```

### 2. Organize Documentation (~5 min)
```bash
mkdir -p docs/sessions
mv COMPREHENSIVE_FACT_CHECK_REPORT.md docs/sessions/
mv notebooks/UPDATE_SESSION_SUMMARY.md docs/sessions/
```

### 3. Archive Old Notebooks (~10 min)
```bash
mkdir -p notebooks/archive
mv notebooks/RESEARCH_REPORT.ipynb notebooks/archive/
mv notebooks/RESEARCH_REPORT_CONDENSED.ipynb notebooks/archive/
mv notebooks/portfolio_trimming_analysis.ipynb notebooks/archive/

cat > notebooks/README.md << 'EOF'
# Notebooks Directory

## Current Notebook (Use This)
**COMPREHENSIVE_BACKTEST_REPORT.ipynb** - Publication-ready analysis
- 42 strategies (5 trim types × 6 reinvestment modes)
- UPDATE 1-3 complete (cost/tax modeling, validation)
- Fact-checked (9.5/10 quality)
- Last Updated: 2025-11-06

## Archived Notebooks
See `archive/` for historical versions from Phase 1-4.
EOF
```

### 4. Archive Diagnostic Scripts (~5 min)
```bash
mkdir -p src/utils/archive
mv src/utils/investigate_warnings.py src/utils/archive/
mv src/utils/diagnose_metrics_bug.py src/utils/archive/
mv src/utils/investigate_issues.py src/utils/archive/
mv src/utils/compare_mock_vs_real.py src/utils/archive/
mv src/utils/generate_mock_data.py src/utils/archive/
mv src/utils/verify_cagr_trading_days.py src/utils/archive/
mv src/utils/check_cagr_calculation.py src/utils/archive/
```

### 5. Git Commit Cleanup (~5 min)
```bash
git add -A
git commit -m "Organizational cleanup: Archive temporary scripts and old files

MOVED TO ARCHIVES:
- 5 temporary notebook fix scripts → scripts/archive/
- 2 session documents → docs/sessions/
- 3 old notebooks → notebooks/archive/
- 7 diagnostic utils → src/utils/archive/

ADDED READMEs:
- scripts/archive/README.md
- notebooks/README.md

STATUS: Project structure clean, ready for public release
"
```

### 6. Update README (Optional, ~10 min)

Add UPDATE 3 section to README.md - see `ORGANIZATIONAL_CLEANUP_PLAN.md` for template text.

---

## ⚡ FASTEST PATH (If Short on Time)

Just run these 3 commands:
```bash
# Archive everything
mkdir -p scripts/archive docs/sessions notebooks/archive src/utils/archive
mv notebooks/*.py scripts/archive/
mv COMPREHENSIVE_FACT_CHECK_REPORT.md docs/sessions/
mv notebooks/UPDATE_SESSION_SUMMARY.md docs/sessions/
mv notebooks/{RESEARCH_REPORT,RESEARCH_REPORT_CONDENSED,portfolio_trimming_analysis}.ipynb notebooks/archive/
mv src/utils/{investigate_*,diagnose_*,compare_*,generate_mock*,verify_*,check_*}.py src/utils/archive/ 2>/dev/null

# Commit
git add -A && git commit -m "chore: Archive temporary and old files"

# Done in 2 minutes
```

---

## 🔍 HOW TO VERIFY

After cleanup, your directory should look like:
```
trim_strat_test/
├── notebooks/
│   ├── COMPREHENSIVE_BACKTEST_REPORT.ipynb  (ONLY current notebook)
│   ├── README.md
│   └── archive/  (3 old notebooks)
├── docs/
│   ├── COST_TAX_MODELING.md
│   ├── CASH_HANDLING_LOGIC.md
│   └── sessions/  (2 session docs)
├── scripts/
│   └── archive/  (5 temporary scripts)
└── src/utils/
    ├── download_with_cache.py  (keep)
    ├── download_data_slowly.py  (keep)
    └── archive/  (7 diagnostic scripts)
```

Check with:
```bash
ls notebooks/  # Should show only COMPREHENSIVE_BACKTEST_REPORT.ipynb and archive/
ls docs/sessions/  # Should show both session docs
ls scripts/archive/  # Should show 5 .py files
```

---

## 📝 AFTER CLEANUP

Optional next steps:
1. **Test notebook execution** (if you fix jupyter environment)
2. **Export to PDF/HTML** for sharing
3. **Publish to GitHub** (project is clean and professional)
4. **Run with costs enabled** (set toggles to 0.1% + 20%)
5. **Test 10% trim size** (sensitivity analysis showed it's better)

---

## 🆘 IF YOU GET STUCK

- **Full plan**: `ORGANIZATIONAL_CLEANUP_PLAN.md`
- **What was done last session**: `docs/sessions/UPDATE_SESSION_SUMMARY.md`
- **Fact-checker findings**: `docs/sessions/COMPREHENSIVE_FACT_CHECK_REPORT.md`
- **Current notebook**: `notebooks/COMPREHENSIVE_BACKTEST_REPORT.ipynb`

---

**Estimated Time**: 30-45 minutes
**Difficulty**: Easy (just moving files)
**Payoff**: Clean, professional project structure ready for public release 🎯

