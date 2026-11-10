# Does trimming your winners beat buy-and-hold?

When a stock in your portfolio shoots up, the common advice is to "take some profits": sell part of it and spread the money around. I tested that advice on 17,000 random portfolios over twenty years of market history. It does not beat doing nothing.

## Summary

**The question.** Should you sell part of a holding when it runs hot, or leave your portfolio alone? Selling part of a holding is called *trimming*. Leaving everything alone is called *buy-and-hold*.

**The test.** I took two trimming rules and ran each on 17,000 randomly built portfolios of S&P 500 stocks, across every five-year period starting from 2003 to 2019. The stock lists contain no hindsight, and the data includes companies that later went bankrupt.

**What I found.**

1. **Trimming is a coin flip.** A rule that sells holdings when they turn unusually volatile beat buy-and-hold 48.4% of the time. A rule that sells holdings once they have doubled beat it 49.9% of the time.
2. **The typical difference is close to zero.** Half of all portfolios ended within one percentage point a year of buy-and-hold.
3. **Trimming after a double helps a little on risk, and that is all it does.** It left returns unchanged and improved risk-adjusted return in 57% of cases. Taxes, which this test leaves out, would eat into even that.
4. **A single portfolio can tell you the opposite, and be wrong.** On one hand-picked portfolio, the first rule beat buy-and-hold by 52%. That result was luck, and this page shows exactly where the luck came from.

**The answer.** Neither rule has an edge. If you test a trading idea on one portfolio, you are measuring that portfolio, not the idea.

![Histogram of results for 15,511 random portfolios. Most sit close to zero.](charts/05_random_portfolios_finsaber.png)

*Each bar counts random portfolios. Right of zero, the volatility rule beat buy-and-hold. Left of zero, it lost. The peak sits on zero. The bar at each end holds the few cases that fall outside the chart.*

This project studies a method. It is not investment advice.

## The terms, in plain words

You need six ideas to follow the rest.

**Backtest.** A replay of history. You take a rule, apply it to old prices day by day, and see how much money it would have made. A backtest tells you what worked in the past, on the data you gave it. It promises nothing about the future.

**Buy-and-hold.** Buy your stocks on day one and never trade. This is the baseline that every strategy has to beat.

**Trimming.** Selling part of one holding. In this project a trim always sells 20% of that holding. The money goes straight back into the whole portfolio, split in proportion to what each holding is worth. No cash sits idle.

**Volatility.** How much a price jumps around from day to day, stated as a yearly percentage. A calm stock might have a volatility of 15%. A wild one, 60%.

**Sharpe ratio.** Return divided by volatility: how much you earned for each unit of risk you took. Higher is better. When I say "risk-adjusted return", this is what I mean.

**Maximum drawdown.** The worst fall from a peak to the next low. A drawdown of -46% means that at some point the portfolio was worth 46% less than its earlier high.

## The two rules

**Rule 1: Trim at +100%.** When a holding has doubled since you bought it, sell 20% of it. This is the plain version of "take profits".

**Rule 2: Volatility-2.5x.** Watch each holding separately and compare two numbers:

- how much it has jumped around over the last 30 days, and
- how much it normally jumps around (its typical level over the past two years).

When the first number is more than 2.5 times the second, sell 20% of that holding. In short: *sell some of whatever has suddenly become much wilder than usual.* The idea is that a stock in turmoil is a stock worth owning less of.

For both rules, the money from each sale goes back into the whole portfolio in proportion.

## How the test works

One portfolio over one decade is an anecdote. To learn whether a rule works, you need many portfolios, many periods, and no hindsight.

- **17,000 cases.** For each start year from 2003 to 2019, I drew 1,000 random portfolios of six stocks with random weights, and ran each for five years.
- **No hindsight in the stock list.** A portfolio starting in 2005 can only hold companies that were in the S&P 500 in 2005. Pick from today's list instead and you have already chosen the survivors.
- **Failures included.** The price data includes companies that later collapsed, such as Circuit City, Washington Mutual and Kodak. When a company leaves the market, its holding stays frozen at the last price. In each five-year window, between 22 and 49 of the available companies disappeared.
- **No same-day trading.** Each trade happens the day after its signal, so a rule cannot act on a price it has only just seen.

The code is in `src/random_portfolios.py` and the numbers are in `results/random_portfolios_finsaber.json`.

## Results

Some random portfolios never trigger a trim, which makes them identical to buy-and-hold. The table counts only portfolios where the rule traded at least once.

| Rule | Portfolios that traded | Beat buy-and-hold on return | Beat it on Sharpe ratio | Typical difference in yearly return |
|---|---|---|---|---|
| Trim at +100% | 15,030 | 49.9% | 57.0% | 0.00 points |
| Volatility-2.5x | 15,511 | 48.4% | 45.9% | -0.03 points |

- **Trim at +100% changes almost nothing.** Returns match buy-and-hold. Nine in ten cases land within one point a year either way. It improves the Sharpe ratio a little more than half the time. Every trim of a winner also creates a tax bill, which this test ignores, so in real life that small benefit would shrink.
- **Volatility-2.5x is a coin flip that costs a little.** It wins 48.4% of the time, and on average it gives up 0.20 points of return a year. Half of all cases land within one point a year of buy-and-hold. Nine in ten land between -4.4 and +3.7 points.

### The period matters more than the rule

Results swing with the start year. Volatility-2.5x won 65% of the time for portfolios starting in 2014 and 29% for those starting in 2018.

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

The four worst start years for Volatility-2.5x are 2016 to 2019, the ones whose five-year windows contain the 2020 crash. The rule sells what turns wild, and in March 2020 nearly everything turned wild near the bottom. Selling then cost most portfolios return.

So a rule can look good or bad depending on which years you happen to test. That is one more reason not to trust a single run.

## How one portfolio can fool you

Here is a case that shows the danger. It was my first test of these rules, and for a while I believed it.

Take $100,000, split six ways, and hold it from January 2015 to November 2024:

| S&P 500 fund (SPY) | Nasdaq fund (QQQ) | S&P 500 fund (VOO) | Apple | Microsoft | Tesla |
|---|---|---|---|---|---|
| 30% | 20% | 10% | 15% | 15% | 10% |

On this portfolio, Volatility-2.5x crushes buy-and-hold:

| | Final value | Yearly return | Sharpe ratio | Worst drawdown |
|---|---|---|---|---|
| Buy-and-hold | $688,711 | 21.69% | 0.90 | -46.3% |
| Volatility-2.5x | $1,046,173 | 26.98% | 0.86 | -62.4% |

![Portfolio value over time for both strategies](charts/01_value.png)

That is 52% more money, or 5.3 percentage points a year. Among the 15,511 random cases above, only 2.3% beat buy-and-hold by that much, about 1 in 43. If this were your only test, you would think you had found something. Four questions show that you had not. The code is in `src/audit.py` and the numbers are in `results/audit.json`.

### Question 1: What did the rule sell?

It made 47 trims in ten years. Not one was Tesla, the portfolio's biggest winner.

![Number of trims for each holding. Tesla has zero.](charts/03_trims.png)

The reason is in how the rule measures "wilder than usual". It compares each holding with its own normal:

| Holding | Normal volatility | Peak in the 2020 crash | Peak ÷ normal | Crossed 2.5? |
|---|---|---|---|---|
| SPY (S&P 500 fund) | 15% | 82% | 5.4 | Yes |
| Apple | 31% | 96% | 3.1 | Yes |
| Tesla | 57% | 139% | 2.4 | **Never, in ten years** |

Tesla was the wildest holding by far. But it was always wild, so the rule never saw it as unusual. Every trim fell on the calmer holdings, in two market panics: 18 trims in 2018 and 29 in 2020.

### Question 2: Where did the money go?

Each trim put money back into all six holdings. So every time the rule sold an index fund, it bought a little more of everything else, Tesla included.

- Before the 2020 crash, Tesla was 22% of the portfolio.
- Four months later it was 49%.
- By November 2021 it was 77%. Under buy-and-hold it was 41%.
- By the end, the three index funds had shrunk to 10% of the portfolio. Under buy-and-hold they were 34%.

![Tesla's share of the portfolio under each strategy](charts/02_tsla_weight.png)

The rule ended up holding 3.77 times as many Tesla shares as it started with, most of them bought in the spring of 2020. From its low that March, Tesla's price rose 17-fold by late 2021.

So on this portfolio the rule did not "reduce exposure to turmoil". By accident, it sold index funds in a crash and bought Tesla at the best possible moment. The table above already hinted at this: the winning rule had a lower Sharpe ratio and a deeper drawdown. It made more money by taking more risk.

### Question 3: Does the rule still win without Tesla?

Remove Tesla, share its 10% among the other five holdings, and run it again.

| Five holdings, no Tesla | Final value | Sharpe ratio | Worst drawdown |
|---|---|---|---|
| Buy-and-hold | $580,686 | 0.94 | -30.1% |
| Volatility-2.5x | $690,876 | 0.97 | -32.1% |

The edge drops from 52% to 19%. What remains is the same move on a smaller scale: out of index funds and into Apple and Microsoft, during a decade when both beat the index.

### Question 4: Does the win survive a small change?

![Final value under each variation, with buy-and-hold as a reference line](charts/04_tests.png)

- **Set the trigger at 1.5 instead of 2.5** and the rule ends at $541,437. That is worse than buy-and-hold.
- **Skip the trims between February and June 2020** and it ends at $852,103. Five months produced about half the win.

A result that depends on one stock, one setting and one five-month stretch is not a strategy. It is a description of what happened to one portfolio.

### The same portfolio, in the big test

I also ran this six-holding portfolio through the five-year windows of the big test. It beat buy-and-hold by 1.8 to 21.8 points a year for start years 2015 to 2020. The typical random portfolio in the same windows stayed within one point of buy-and-hold. This portfolio stood apart every time, for the same reason every time.

## Five questions to ask of any backtest

1. **What did it trade?** Read the trade list. Does it match the story being told?
2. **Where did the money end up?** Check whether one holding grew to dominate.
3. **Does it survive losing its best holding?** Remove it and run again.
4. **Does it survive a small change?** Move one setting. Drop the best few months.
5. **Does it work on portfolios nobody chose?** One portfolio is a story. Thousands give you a rate.

A check that the numbers add up is not on this list, because it is not enough. A result can be reported with perfect accuracy and still mean nothing. When I first ran the single-portfolio case, an AI reviewer confirmed every figure in my write-up and passed it. The figures were right. The conclusion was wrong. Checking that results are *consistent* and checking *why* they came out that way are two different jobs.

## Can the data be trusted?

The prices come from [FINSABER](https://huggingface.co/datasets/waylonli/FINSABER-data), a research dataset on Hugging Face with 1,017 stocks from 2000 to 2024. A third of them (334) stopped trading before mid-2024. The dataset does not say where its prices came from, so I checked it two ways.

- **Against a second source.** For the 102 stocks that also appear in a Yahoo Finance download, I compared daily returns. For 100 of them the two sources agree almost exactly (a correlation of 0.999 or better). The code is in `src/compare_sources.py`.
- **For broken records.** Some ticker symbols get reused: a company dies, and years later a different company takes its symbol. In the raw file, one such stock appeared to go from $7.73 to $141,630 overnight. I wrote two rules to catch this, removed 37 stocks, and cut 59 short at the point where the record broke. The repair barely moved the result: the volatility rule won 48.9% of the time before and 48.4% after.

After the repair, the test covers 78% to 96% of the S&P 500, depending on the year.

**A second opinion.** I repeated the whole test on different data: Yahoo Finance prices for 103 large companies, chosen as of the end of 2014, for start years 2015 to 2021. Volatility-2.5x won 42.9% of the time. Two tests on different data gave the same answer.

## Run it yourself

Everything is free: no account, no API key. You need Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python tests/test_engine.py                  # 11 checks

python src/download_finsaber.py              # prices for the main test, about 250 MB
python src/random_portfolios.py finsaber     # the main test, about 2 minutes

python src/audit.py                          # the single-portfolio case

python src/download_universe.py              # prices for the second opinion
python src/random_portfolios.py yahoo        # the second opinion
python src/compare_sources.py                # FINSABER against Yahoo
```

The prices for the single-portfolio case are already in `data/`.

## What is in this repository

```
src/engine.py              signals, simulation, performance measures
src/random_portfolios.py   the main test: 17,000 random portfolios
src/audit.py               the single-portfolio case and its four questions
src/download_finsaber.py   price download for the main test
src/universe.py            stock list for the second opinion
src/download_universe.py   price download for the second opinion
src/compare_sources.py     FINSABER prices against Yahoo prices
src/plots.py               chart style
tests/test_engine.py       11 checks
data/sp500_members.csv     who was in the S&P 500, and when
results/                   every number quoted on this page
charts/                    every chart on this page
original/                  an earlier version of this project, kept for reference
```

## Limits

- **No costs, no tax.** Real trading costs money, and trimming a winner triggers tax. Both would make every trimming rule look worse than it does here.
- **Two rules, one trim size.** I tested two triggers, each selling 20%. Other triggers and sizes might behave differently, though nothing here suggests they would.
- **The 17,000 cases overlap.** A window starting in 2010 shares four years with one starting in 2011. The cases are many but not independent, so read the percentages as a guide, not a precise measurement.
- **Some companies are missing.** The price data covers 78% to 96% of the index. It has some well-known failures but not others: I could not find Lehman Brothers or the old General Motors in it. The missing companies are probably not a random sample.
- **Dead companies freeze.** A holding in a company that leaves the market stays at its last price. That is right for a bankruptcy. For a buyout it means the cash sits idle, which slightly understates returns for both strategies.
- **The price source is unverified for failed companies.** My check against Yahoo covers large survivors since 2012. I could not check the failed companies against anything.
- **US large companies only, 2003 to 2024.** Other markets and other eras may differ.

## Data sources

- **FINSABER prices:** [waylonli/FINSABER-data](https://huggingface.co/datasets/waylonli/FINSABER-data) on Hugging Face, Apache-2.0 license. Not stored here; `src/download_finsaber.py` fetches it.
- **S&P 500 membership history:** `data/sp500_members.csv` is `sp500_ticker_start_end.csv` from [fja05680/sp500](https://github.com/fja05680/sp500), MIT license, copyright (c) 2019-2020 Farrell J. Aultman.
- **Yahoo Finance prices:** through the `yfinance` package.
