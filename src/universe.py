"""The stock universe for the random-portfolio test.

LARGE_CAPS_2014 is a list of 103 of the largest S&P 500 companies at the
end of 2014. The list is compiled by hand. It is not an official index list.
The date is important: a list from today knows which companies won. This list
does not. It includes companies that later did badly (GE, IBM, INTC, T, F).

Tickers are the symbols in use today (META was FB, RTX was UTX, ELV was ANTM,
BKNG was PCLN, BNY was BK).

LEFT_THE_MARKET lists large companies from the end of 2014 that were later
acquired or merged. Free price data does not have them, so the test cannot
use them. This is the survivorship bias that stays in the test.
"""

LARGE_CAPS_2014 = [
    "AAPL", "XOM", "MSFT", "GOOGL", "BRK-B", "JNJ", "WFC", "WMT", "GE", "PG",
    "JPM", "CVX", "VZ", "META", "KO", "PFE", "T", "ORCL", "INTC", "BAC",
    "MRK", "DIS", "C", "V", "IBM", "GILD", "HD", "AMZN", "CSCO", "PEP",
    "CMCSA", "PM", "QCOM", "UNH", "AMGN", "CVS", "SLB", "MMM", "UNP", "BA",
    "MA", "MO", "RTX", "MCD", "ABBV", "BMY", "AXP", "USB", "GS",
    "COP", "BIIB", "UPS", "LLY", "MDT", "HON", "NKE", "LOW", "SBUX", "MS",
    "AIG", "EBAY", "CL", "F", "ACN", "COST", "TXN", "OXY", "BLK", "MDLZ",
    "HPQ", "BKNG", "ABT", "DHR", "TMO", "GM", "KMI", "LMT", "CAT", "MET",
    "SPG", "DUK", "EOG", "TGT", "PNC", "NEE", "BNY", "COF", "TJX", "FDX",
    "AMT", "ELV", "DE", "GD", "EMR", "SO", "HAL", "PSX", "ADP", "D",
    "EXC", "KMB", "CRM", "DD",
]

LEFT_THE_MARKET = [
    "CELG", "AGN", "TWX", "EMC", "MON", "ESRX", "APC", "KRFT", "FOXA", "PCP", "AET", "WBA",
]

INDEX_FUNDS = ["SPY", "QQQ"]

# The original portfolio also needs TSLA and VOO. They are not in the random draw.
ORIGINAL_PORTFOLIO = {"SPY": 0.30, "QQQ": 0.20, "VOO": 0.10, "AAPL": 0.15, "MSFT": 0.15, "TSLA": 0.10}
EXTRA = ["TSLA", "VOO"]

RANDOM_DRAW = LARGE_CAPS_2014 + INDEX_FUNDS
DOWNLOAD = RANDOM_DRAW + EXTRA
