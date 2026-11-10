# The 52% win that was luck

I built a backtest that seemed to show a way to beat buy-and-hold by 52%. A year later I audited it. The win was real on paper and worthless as advice. This repository shows how I found that out.

## Summary

**The question.** When a stock in your portfolio does well, should you sell part of it and spread the money around, or leave it alone? Selling part of a holding is called *trimming*. Leaving everything alone is called *buy-and-hold*.

**What I found the first time (2025).** I tested 42 trimming rules on one portfolio over ten years. One rule turned $100,000 into $1,046,173. Buy-and-hold made $688,711. That is 52% more money. An AI fact-checker reviewed my report and scored it 8.5 out of 10. I published it.

**What I found when I checked (2026).**

1. **The rule never did what I said it did.** I described it as "taking profits". In ten years it never once sold the portfolio's biggest winner, Tesla. It sold index funds during the 2020 crash and used the money to buy more Tesla, just before Tesla rose 17-fold.
2. **The win was fragile.** Change one setting and the same rule loses to buy-and-hold.
3. **The AI fact-checker missed all of it.** It confirmed that the numbers in my report matched my results file. It never asked why the results came out that way.
4. **A fair test shows a coin flip.** I ran the same rule on 17,000 random portfolios, including companies that later went bankrupt. It beat buy-and-hold 48.4% of the time.

**The answer.** The rule has no edge. My portfolio got lucky, and I mistook luck for a finding.

![Histogram of results for 15,511 random portfolios. Most sit close to zero.](charts/05_random_portfolios_finsaber.png)

*Each bar counts random portfolios. Right of zero, the trimming rule beat buy-and-hold. Left of zero, it lost. The peak sits on zero. My original result, 5.3 points a year to the right, beat 97.7% of them. The bar at each end holds the few cases that fall outside the chart.*

This project studies a method. It is not investment advice.

## The terms, in plain words

You need six ideas to follow the rest.

**Backtest.** A replay of history. You take a rule, apply it to old prices day by day, and see how much money it would have made. A backtest tells you what worked in the past, on the data you gave it. It promises nothing about the future.

**Buy-and-hold.** Buy your stocks on day one and never trade. This is the baseline that every strategy has to beat.

**Trimming.** Selling part of one holding. In this project a trim always sells 20% of that holding. The money goes straight back into the whole portfolio, split in proportion to what each holding is worth. No cash sits idle.

**Volatility.** How much a price jumps around from day to day, stated as a yearly percentage. A calm stock might have a volatility of 15%. A wild one, 60%.

**The "Volatility-2.5x" rule.** This is the rule that won. It watches each holding separately and compares two numbers:

- how much the holding has jumped around over the last 30 days, and
- how much it normally jumps around (its typical level over the past two years).

When the first number is more than 2.5 times the second, the rule trims that holding. In short: *sell some of whatever has suddenly become much wilder than usual.*

Everything on this page turns on one detail. "Wilder than usual" is measured against each holding's own normal:

| Holding | Normal volatility | Peak in the 2020 crash | Peak ÷ normal | Crossed 2.5? |
|---|---|---|---|---|
| SPY (S&P 500 fund) | 15% | 82% | 5.4 | Yes |
| Apple | 31% | 96% | 3.1 | Yes |
| Tesla | 57% | 139% | 2.4 | **Never, in ten years** |

Tesla was the wildest holding by far. But it was always wild, so the rule never saw it as unusual.

**Sharpe ratio and drawdown.** Two ways to measure risk. The Sharpe ratio is return divided by volatility: how much you earned for each unit of risk you took. Higher is better. Maximum drawdown is the worst fall from a peak to the next low. A drawdown of -46% means that at some point the portfolio was worth 46% less than its earlier high.

## Part 1: The result I published

The portfolio was $100,000, split six ways, held from January 2015 to November 2024:

| S&P 500 fund (SPY) | Nasdaq fund (QQQ) | S&P 500 fund (VOO) | Apple | Microsoft | Tesla |
|---|---|---|---|---|---|
| 30% | 20% | 10% | 15% | 15% | 10% |

| | Final value | Yearly return | Sharpe ratio | Worst drawdown |
|---|---|---|---|---|
| Buy-and-hold | $688,711 | 21.69% | 0.90 | -46.3% |
| Volatility-2.5x | $1,046,173 | 26.98% | 0.86 | -62.4% |

![Portfolio value over time for both strategies](charts/01_value.png)

Two warning signs were already in this table, and I ignored both. The winning rule had a *lower* Sharpe ratio and a *deeper* drawdown. It made more money by taking more risk.

My explanation at the time was that the rule "let winners run", raised cash before the 2020 crash, and bought back at the bottom. None of that was true.

## Part 2: The audit

I rebuilt the engine from scratch and matched the original numbers to the dollar. Then I asked four questions. The code is in `src/audit.py` and the numbers are in `results/audit.json`.

### Question 1: What did the rule sell?

It made 47 trims in ten years. Not one was Tesla.

![Number of trims for each holding. Tesla has zero.](charts/03_trims.png)

Every trim happened in one of two market panics: 18 in 2018 and 29 in 2020. In a panic, index funds become far wilder than their calm normal, so the rule sold them. Tesla never crossed its own high bar.

### Question 2: Where did the money go?

Each trim put money back into all six holdings. So every time the rule sold an index fund, it bought a little more of everything else, Tesla included.

- Before the 2020 crash, Tesla was 22% of the portfolio.
- Four months later it was 49%.
- By November 2021 it was 77%. Under buy-and-hold it was 41%.
- By the end, the three index funds had shrunk to 10% of the portfolio. Under buy-and-hold they were 34%.

![Tesla's share of the portfolio under each strategy](charts/02_tsla_weight.png)

The rule ended up holding 3.77 times as many Tesla shares as it started with, most of them bought in the spring of 2020. From its low that March, Tesla's price rose 17-fold by late 2021.

So the strategy was never "take profits from winners". By accident, it was "sell index funds in a crash and buy Tesla". That also explains the deeper drawdown: when Tesla fell in 2022, most of the portfolio fell with it.

### Question 3: Does the rule still win without Tesla?

I removed Tesla, shared its 10% among the other five holdings, and ran everything again.

| Five holdings, no Tesla | Final value | Sharpe ratio | Worst drawdown |
|---|---|---|---|
| Buy-and-hold | $580,686 | 0.94 | -30.1% |
| Volatility-2.5x | $690,876 | 0.97 | -32.1% |

The edge drops from 52% to 19%. Most of the win came from Tesla, but not all. What remains is the same move on a smaller scale: out of index funds and into Apple and Microsoft, during a decade when both beat the index. One portfolio cannot tell me whether that is a real effect or more luck. Part 5 answers that.

### Question 4: Does the win survive a small change?

![Final value under each variation, with buy-and-hold as a reference line](charts/04_tests.png)

- **Set the trigger at 1.5 instead of 2.5** and the rule ends at $541,437. That is worse than buy-and-hold.
- **Skip the trims between February and June 2020** and it ends at $852,103. Five months produced about half the win.
- **Trade a day later**, so the rule cannot act on a price it has only just seen, and it ends at $1,038,336. This made little difference, which rules out one common backtest error.

A result that depends on one setting and one five-month stretch is not a strategy. And I had tried 42 rules and reported the best one. Try 42 of anything on a single portfolio and one of them will look brilliant.

## Part 3: The bugs

While rebuilding the engine I found three errors in the original (`original/run_backtest_index_focus.py`).

**1. Cash was counted on days it did not exist.** Some of the 42 rules hold cash for a while after a trim. The engine took the cash balance from the *last* day and added it to *every* day. Final values were right, but the day-by-day record was wrong. That puts the risk numbers for 28 of the 42 rules in doubt.

| Rule | Sharpe, original | Sharpe, fixed | Worst drawdown, original | Worst drawdown, fixed |
|---|---|---|---|---|
| Trim at +50%, hold cash | 0.48 | 0.98 | -24.7% | -26.1% |
| Trim at +100%, hold cash | 0.61 | 0.96 | -30.0% | -32.8% |
| Volatility-2.5x, hold cash until calm | 0.78 | 0.87 | -59.7% | -44.4% |

My report said the cash-holding rules "destroyed returns". On return alone that holds up: the first rule above ended at $443,061, well behind buy-and-hold. But the bug hid the other half of the story. With cash counted correctly, that rule has a Sharpe ratio of 0.98, better than buy-and-hold's 0.90. It earned less and risked much less.

**2. The Sharpe ratio was not what the report said.** The report claimed a 2% risk-free rate. The code used 0%. With 2%, buy-and-hold scores 0.82 and the winning rule 0.80.

**3. One rule was supposed to earn interest on its cash and never did.** The code set a 4% rate and then did not use it.

## Part 4: What the AI fact-checker missed

The 2025 project used four AI agents: one to write the report, one to adjust the tone, one to check facts, and one to apply corrections. The fact-checker's review is in `original/FACT_CHECK_REPORT_DC_VOICE.md`. Its verdict was "Pass with Minor Revisions", 8.5 out of 10.

It did real work. It compared every number in the report with the results file. It recalculated the yearly returns. It challenged loose wording.

But it asked only one kind of question: *does the report match the results?* It never asked the other kind: *why are the results what they are?* It did not read the list of trades. It did not ask which holding made the money. It did not open the engine code, so it could not find the bugs.

I do not blame the tool. I asked it to check my report, and it did. The mistake was mine: I treated "the numbers are consistent" as if it meant "the conclusion is right". Those are different claims, and only the first had been tested.

This is one case, not a study of AI fact-checking. But it changed how I use these tools. I now ask for the cause check as well as the consistency check, and for anything that matters I do the cause check myself.

## Part 5: The fair test

One portfolio over one decade is an anecdote. To learn whether the rule works, I needed many portfolios, many periods, and no hindsight.

**How the test works**

- **17,000 cases.** For each start year from 2003 to 2019, I drew 1,000 random portfolios of six stocks with random weights, and ran each for five years.
- **No hindsight in the stock list.** A portfolio starting in 2005 can only hold companies that were in the S&P 500 in 2005. Pick from today's list instead and you have already chosen the survivors.
- **Failures included.** The price data includes companies that later collapsed, such as Circuit City, Washington Mutual and Kodak. When a company leaves the market, its holding stays frozen at the last price. In each five-year window, between 22 and 49 of the available companies disappeared.
- **Two rules tested:** Volatility-2.5x, and a simpler rule that trims a holding once it has doubled ("Trim at +100%").
- **Honest trading.** Each trade happens the day after its signal.

The code is in `src/random_portfolios.py` and the numbers are in `results/random_portfolios_finsaber.json`.

**What it shows**

Some random portfolios never trigger a trim, which makes them identical to buy-and-hold. The table counts only portfolios where the rule traded at least once.

| Rule | Portfolios that traded | Beat buy-and-hold on return | Beat it on Sharpe ratio | Typical difference in yearly return |
|---|---|---|---|---|
| Volatility-2.5x | 15,511 | 48.4% | 45.9% | -0.03 points |
| Trim at +100% | 15,030 | 49.9% | 57.0% | 0.00 points |

- **Volatility-2.5x is a coin flip that costs a little.** It wins 48.4% of the time, and on average it gives up 0.20 points of return a year.
- **Usually it barely matters.** Half of all cases land within one point a year of buy-and-hold. Nine in ten land between -4.4 and +3.7 points.
- **My original result was a 1-in-43 outcome.** It won by 5.3 points a year. Only 2.3% of the random cases did that well.
- **Trim at +100% leaves returns unchanged** and improves the Sharpe ratio a little more than half the time. This test ignores tax, and every trim of a winner creates a tax bill, so in real life even that small benefit would shrink.

**The crash that made my result hurt almost everyone else**

Results swing with the start year. Volatility-2.5x won 65% of the time for portfolios starting in 2014 and 29% for those starting in 2018. The four worst start years are 2016 to 2019, the ones whose five-year windows contain the 2020 crash.

That is the same crash that produced my 52% win. For most portfolios, selling whatever had turned wild in March 2020 cost them return. My portfolio happened to hold Tesla, and the money from those sales went into it.

| Start year | Volatility-2.5x wins | Trim at +100% wins | | Start year | Volatility-2.5x wins | Trim at +100% wins |
|---|---|---|---|---|---|---|
| 2003 | 55.7% | 40.3% | | 2012 | 51.5% | 52.9% |
| 2004 | 55.2% | 57.0% | | 2013 | 63.4% | 49.1% |
| 2005 | 43.8% | 53.7% | | 2014 | 65.1% | 47.4% |
| 2006 | 46.4% | 57.4% | | 2015 | 63.0% | 32.5% |
| 2007 | 50.2% | 57.6% | | 2016 | 39.6% | 35.1% |
| 2008 | 52.9% | 47.3% | | 2017 | 37.5% | 44.5% |
| 2009 | 38.2% | 51.7% | | 2018 | 28.9% | 66.8% |
| 2010 | 61.4% | 56.8% | | 2019 | 31.2% | 61.3% |
| 2011 | 53.7% | 41.2% | | | | |

**Can the price data be trusted?**

The prices come from [FINSABER](https://huggingface.co/datasets/waylonli/FINSABER-data), a research dataset on Hugging Face with 1,017 stocks from 2000 to 2024. A third of them (334) stopped trading before mid-2024. The dataset does not say where its prices came from, so I checked it two ways.

- **Against a second source.** For the 102 stocks that also appear in my Yahoo Finance download, I compared daily returns. For 100 of them the two sources agree almost exactly (a correlation of 0.999 or better). The code is in `src/compare_sources.py`.
- **For broken records.** Some ticker symbols get reused: a company dies, and years later a different company takes its symbol. In the raw file, one such stock appeared to go from $7.73 to $141,630 overnight. I wrote two rules to catch this, removed 37 stocks, and cut 59 short at the point where the record broke. The repair barely moved the result: 48.9% before, 48.4% after.

After the repair, the test covers 78% to 96% of the S&P 500, depending on the year.

**A second opinion**

I repeated the test on different data: Yahoo Finance prices for 103 large companies, chosen as of the end of 2014, for start years 2015 to 2021. Volatility-2.5x won 42.9% of the time. In the same test, my original six-holding portfolio beat buy-and-hold by 1.8 to 21.8 points a year for start years 2015 to 2020. Two tests on different data gave the same answer: the rule does nothing special, and my portfolio was the exception.

## Five questions I now ask of any backtest

1. **What did it trade?** Read the trade list. Does it match the story being told?
2. **Where did the money end up?** Check whether one holding grew to dominate.
3. **Does it survive losing its best holding?** Remove it and run again.
4. **Does it survive a small change?** Move one setting. Drop the best few months.
5. **Does it work on portfolios nobody chose?** One portfolio is a story. Thousands give you a rate.

## Run it yourself

Everything is free: no account, no API key. You need Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python tests/test_engine.py                  # 11 checks
python src/audit.py                          # Part 2 and Part 3

python src/download_finsaber.py              # prices for Part 5, about 250 MB
python src/random_portfolios.py finsaber     # Part 5, about 2 minutes

python src/download_universe.py              # prices for the second opinion
python src/random_portfolios.py yahoo        # the second opinion
python src/compare_sources.py                # FINSABER against Yahoo
```

The prices for the audit are already in `data/`.

## What is in this repository

```
src/engine.py              signals, simulation, performance measures
src/audit.py               the audit (Parts 2 and 3)
src/random_portfolios.py   the fair test (Part 5)
src/download_finsaber.py   price download for Part 5
src/universe.py            stock list for the second opinion
src/download_universe.py   price download for the second opinion
src/compare_sources.py     FINSABER prices against Yahoo prices
src/plots.py               chart style
tests/test_engine.py       11 checks, one of which reproduces the original result to the dollar
data/sp500_members.csv     who was in the S&P 500, and when
results/                   every number quoted on this page
charts/                    every chart on this page
original/                  the 2025 engine, report and fact-check, untouched
```

## Limits

- **No costs, no tax.** Real trading costs money, and trimming a winner triggers tax. Both would make every trimming rule look worse than it does here.
- **Only two rules got the fair test.** Part 5 covers Volatility-2.5x and Trim at +100%, not the other 40 rules from the original report.
- **The 17,000 cases overlap.** A window starting in 2010 shares four years with one starting in 2011. The cases are many but not independent, so read the percentages as a guide, not a precise measurement.
- **Some companies are missing.** The price data covers 78% to 96% of the index. It has some well-known failures but not others: I could not find Lehman Brothers or the old General Motors in it. The missing companies are probably not a random sample.
- **Dead companies freeze.** A holding in a company that leaves the market stays at its last price. That is right for a bankruptcy. For a buyout it means the cash sits idle, which slightly understates returns for both strategies.
- **The price source is unverified for failed companies.** My check against Yahoo covers large survivors since 2012. I could not check the failed companies against anything.

## Data sources

- **FINSABER prices:** [waylonli/FINSABER-data](https://huggingface.co/datasets/waylonli/FINSABER-data) on Hugging Face, Apache-2.0 license. Not stored here; `src/download_finsaber.py` fetches it.
- **S&P 500 membership history:** `data/sp500_members.csv` is `sp500_ticker_start_end.csv` from [fja05680/sp500](https://github.com/fja05680/sp500), MIT license, copyright (c) 2019-2020 Farrell J. Aultman.
- **Yahoo Finance prices:** through the `yfinance` package. The six files in `data/` come from the original project.
