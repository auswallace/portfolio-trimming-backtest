# Cost & Tax Modeling Documentation

This document explains how to use the transaction cost and capital gains tax toggles in the Portfolio Trimming Strategy Backtest.

**Last Updated**: 2025-11-06
**Feature Added**: UPDATE 3 (November 2025)

---

## Overview

The backtest engine now includes **optional** transaction costs and capital gains tax modeling. These toggles allow you to test how real-world costs impact strategy performance.

**Key Features:**
- ✅ **Toggle-based**: Set to 0 to disable, any value > 0 to enable
- ✅ **Applied to ALL transactions**: Both selling (trims) and buying (reinvestment)
- ✅ **Tracked separately**: View total costs and taxes in results CSV
- ✅ **Capital gains tax only on gains**: No tax deduction for losses

---

## Configuration Parameters

Located in `src/backtest/run_backtest_index_focus.py` (lines 28-30):

```python
# COST & TAX TOGGLES (set to 0 to disable)
TRANSACTION_COST_PCT = 0.0     # 0.001 = 0.1% per trade (both buys and sells)
CAPITAL_GAINS_TAX_RATE = 0.0   # 0.20 = 20% long-term capital gains tax
```

### Transaction Cost (`TRANSACTION_COST_PCT`)
- **Default**: `0.0` (disabled)
- **Format**: Decimal (e.g., `0.001` = 0.1%, `0.005` = 0.5%)
- **Applied to**:
  - **Selling**: Deducted from gross proceeds
  - **Buying**: Deducted from reinvestment amount (reduces shares purchased)

**Typical Values:**
- `0.0005` = 0.05% (Fidelity/Schwab stock trades, essentially free)
- `0.001` = 0.1% (ETF bid-ask spread)
- `0.003` = 0.3% (Active trading, poor execution)

### Capital Gains Tax (`CAPITAL_GAINS_TAX_RATE`)
- **Default**: `0.0` (disabled)
- **Format**: Decimal (e.g., `0.20` = 20%, `0.15` = 15%)
- **Applied to**: Only when selling at a gain (relative to cost basis)
- **Not applied to**: Losses (no tax deduction modeled)

**Typical Values:**
- `0.15` = 15% (Long-term capital gains, lower brackets)
- `0.20` = 20% (Long-term capital gains, higher brackets)
- `0.37` = 37% (Short-term capital gains, highest bracket)

**Note**: This model assumes ALL gains are long-term. Short-term vs long-term logic is not implemented.

---

## How Costs Are Applied

### When Selling (Trimming)

```python
# 1. Calculate gross proceeds
gross_proceeds = shares_to_sell * current_price

# 2. Apply transaction cost
transaction_cost = gross_proceeds * TRANSACTION_COST_PCT
proceeds_after_cost = gross_proceeds - transaction_cost

# 3. Calculate capital gain
cost_for_shares_sold = shares_to_sell * cost_basis
capital_gain = proceeds_after_cost - cost_for_shares_sold

# 4. Apply capital gains tax (only on gains)
if capital_gain > 0:
    capital_gains_tax = capital_gain * CAPITAL_GAINS_TAX_RATE
else:
    capital_gains_tax = 0

# 5. Net proceeds available for reinvestment
net_proceeds = proceeds_after_cost - capital_gains_tax
```

### When Buying (Reinvesting)

```python
# Apply transaction cost when reinvesting
amount_after_buy_cost = net_proceeds * (1 - TRANSACTION_COST_PCT)
shares_to_buy = amount_after_buy_cost / current_price
```

**Result**: Both sell-side and buy-side transaction costs compound, reducing net shares acquired.

---

## Impact on Results

### New Metrics Added

The results CSV now includes:
- `total_transaction_costs` - Sum of all transaction costs (both buys and sells)
- `total_capital_gains_tax` - Sum of all capital gains taxes paid
- `total_costs_and_taxes` - Combined total

### Expected Impact

**Transaction Costs (0.1% per trade)**:
- High-frequency strategies (volatility-based): -1.5% to -3% CAGR
- Threshold strategies (Trim@+100%): -0.3% to -0.8% CAGR
- Buy-and-Hold: $0 costs (no trades after initial purchase)

**Capital Gains Tax (20%)**:
- Trim@+50%: -2% to -4% CAGR (frequent trims at lower gains)
- Trim@+100%: -3% to -5% CAGR (larger gains per trim)
- Volatility-based: -4% to -8% CAGR (frequent trims)
- Buy-and-Hold: $0 tax until final sale (not modeled)

**Combined (0.1% costs + 20% tax)**:
- Total impact: -3% to -11% CAGR for trimming strategies
- Buy-and-Hold advantage increases dramatically

---

## Example Scenarios

### Scenario 1: No Costs (Current Default)
```python
TRANSACTION_COST_PCT = 0.0
CAPITAL_GAINS_TAX_RATE = 0.0
```
**Use case**: Academic comparison, ideal scenario

**Results**:
- Volatility-2.5x (pro-rata): 26.98% CAGR
- Buy-and-Hold: 21.69% CAGR
- **Winner**: Trimming by +5.29%

---

### Scenario 2: Low Costs (Modern Brokerage)
```python
TRANSACTION_COST_PCT = 0.0005  # 0.05% (essentially free trading)
CAPITAL_GAINS_TAX_RATE = 0.15  # 15% long-term capital gains
```
**Use case**: Realistic for tax-advantaged accounts (Roth IRA = 0% tax)

**Expected Results**:
- Volatility-2.5x (pro-rata): ~25.5% CAGR (-1.5% from costs/taxes)
- Buy-and-Hold: 21.69% CAGR (unchanged)
- **Winner**: Likely still trimming by ~+3.8%

---

### Scenario 3: Realistic Costs (Taxable Account)
```python
TRANSACTION_COST_PCT = 0.001  # 0.1% (bid-ask spread)
CAPITAL_GAINS_TAX_RATE = 0.20  # 20% long-term capital gains
```
**Use case**: Most realistic for high-income investors in taxable accounts

**Expected Results**:
- Volatility-2.5x (pro-rata): ~23% CAGR (-4% from costs/taxes)
- Buy-and-Hold: 21.69% CAGR (unchanged)
- **Winner**: Still trimming, but margin shrinks to ~+1.3%

---

### Scenario 4: High Costs (Active Trading)
```python
TRANSACTION_COST_PCT = 0.003  # 0.3% (poor execution, slippage)
CAPITAL_GAINS_TAX_RATE = 0.37  # 37% short-term capital gains
```
**Use case**: Worst-case scenario (frequent trading, high bracket, poor execution)

**Expected Results**:
- Volatility-2.5x (pro-rata): ~19% CAGR (-8% from costs/taxes)
- Buy-and-Hold: 21.69% CAGR (unchanged)
- **Winner**: Buy-and-Hold by +2.7%

---

## Limitations & Assumptions

### What IS Modeled:
✅ Transaction costs on ALL trades (both buys and sells)
✅ Capital gains tax on trim proceeds
✅ Cost basis tracking (FIFO-like, per ticker)
✅ Total costs/taxes tracked and reported

### What IS NOT Modeled:
❌ **Short-term vs long-term capital gains** - All gains assumed long-term
❌ **Tax loss harvesting** - No offsetting losses against gains
❌ **Wash sale rules** - Can rebuy immediately after selling
❌ **Final liquidation tax** - Buy-and-hold final sale tax not calculated
❌ **Dividend taxes** - Dividends are reinvested price data, not tracked separately
❌ **State taxes** - Only federal capital gains tax
❌ **Interest on cash** - Cash holdings earn 0%

### Key Assumption: **Buy-and-Hold Final Sale Tax Is Ignored**

This creates an **unfair advantage** for buy-and-hold in taxable accounts:
- Trimming strategies pay taxes throughout 10 years
- Buy-and-hold defers ALL taxes until final sale
- True comparison requires adding ~15-20% tax to buy-and-hold final value

**Example**:
```
Buy-and-Hold final value: $688,711
Minus 20% capital gains tax: $550,969 (net after-tax)
Trimming strategy: $600,000 (after paying taxes throughout)
Winner: Actually trimming, not buy-and-hold
```

**Recommendation**: For fair comparison in taxable accounts, either:
1. Deduct 15-20% from buy-and-hold final value, OR
2. Compare only in tax-advantaged accounts (Roth IRA), OR
3. Use tax-aware strategies (e.g., hold winners >1 year before trimming)

---

## Usage Examples

### Example 1: Test Impact of Transaction Costs Only

```python
# Set costs, no taxes
TRANSACTION_COST_PCT = 0.001  # 0.1%
CAPITAL_GAINS_TAX_RATE = 0.0  # Disabled

# Run backtest
python src/backtest/run_backtest_index_focus.py
```

Compare `results_index_focus/index_focus_results.csv` to baseline (both 0.0).

---

### Example 2: Test Impact of Taxes Only

```python
# No costs, just taxes
TRANSACTION_COST_PCT = 0.0    # Disabled
CAPITAL_GAINS_TAX_RATE = 0.20 # 20%

# Run backtest
python src/backtest/run_backtest_index_focus.py
```

---

### Example 3: Full Realistic Modeling

```python
# Both costs and taxes
TRANSACTION_COST_PCT = 0.001  # 0.1%
CAPITAL_GAINS_TAX_RATE = 0.20 # 20%

# Run backtest
python src/backtest/run_backtest_index_focus.py
```

Check `total_costs_and_taxes` column in results to see total drag.

---

## Interpreting Results

### Key Metrics to Compare:

1. **Final Value** - Net after all costs/taxes
2. **CAGR** - Annualized return (accounts for costs/taxes)
3. **Total Costs & Taxes** - Dollar amount lost to friction
4. **Cost as % of Gains** - `total_costs_and_taxes / (final_value - initial_capital)`

### When Trimming Still Wins:

If costs/taxes < performance advantage, trimming still outperforms:
```
Trimming CAGR - Buy&Hold CAGR > Drag from costs/taxes
```

**Example**:
- No costs: Trimming 26.98%, B&H 21.69% → +5.29% advantage
- With costs: Trimming drag = -4% → Net advantage still +1.29%
- **Verdict**: Trimming wins (barely)

### When Buy-and-Hold Wins:

If costs/taxes > performance advantage, buy-and-hold is better:
```
Drag from costs/taxes > Trimming CAGR - Buy&Hold CAGR
```

**Example**:
- No costs: Trimming 22%, B&H 21.69% → +0.31% advantage
- With costs: Trimming drag = -1.5% → Net advantage = -1.19%
- **Verdict**: Buy-and-hold wins

---

## Best Practices

### For Backtesting Research:
1. **Run baseline first** (both toggles = 0.0) to understand pure strategy performance
2. **Add costs incrementally** (test costs alone, then taxes alone, then combined)
3. **Document your assumptions** (which cost/tax rates you used)
4. **Compare apples-to-apples** (remember B&H doesn't pay final sale tax in current model)

### For Real-World Application:
1. **Use your actual costs** (check your brokerage's fee schedule)
2. **Use your actual tax bracket** (15%, 20%, or 37% federal + state)
3. **Consider account type**:
   - Roth IRA: Set `CAPITAL_GAINS_TAX_RATE = 0.0`
   - Traditional IRA: Set to ordinary income rate (25-37%)
   - Taxable: Set to capital gains rate (15-20%)
4. **Test sensitivity** (run at low/medium/high cost scenarios)

---

## Code References

**Configuration**: `src/backtest/run_backtest_index_focus.py:28-30`
**Sell logic**: `src/backtest/run_backtest_index_focus.py:568-583`
**Buy logic (pro-rata)**: `src/backtest/run_backtest_index_focus.py:613-619`
**Buy logic (drip)**: `src/backtest/run_backtest_index_focus.py:527-534`
**Metrics tracking**: `src/backtest/run_backtest_index_focus.py:666-671`

---

## Future Enhancements

Potential improvements to cost/tax modeling:

1. **Short-term vs long-term capital gains** - Track holding period per share lot
2. **Tax loss harvesting** - Offset gains with losses, track carryforward
3. **Wash sale prevention** - 30-day rule implementation
4. **Final liquidation tax** - Apply tax to buy-and-hold final sale
5. **Dividend tax modeling** - Separate dividend income from price appreciation
6. **State tax support** - Add state capital gains tax rates
7. **Interest on cash** - Model T-bill rates for cash holdings
8. **Dynamic tax rates** - Use historical tax rates by year (2015-2024)
9. **Transaction cost variance** - Different rates for stocks vs ETFs
10. **Slippage modeling** - Market impact on large trades

---

**End of Documentation**
