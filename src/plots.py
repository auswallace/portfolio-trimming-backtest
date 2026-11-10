"""Chart helpers. One style for all charts in this project."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"    # the strategy
ORANGE = "#eb6834"  # buy-and-hold, the reference

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.size": 11, "text.color": TEXT, "axes.labelcolor": TEXT_2,
    "xtick.color": TEXT_2, "ytick.color": TEXT_2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": GRID, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
})


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def two_lines(reference, strategy, reference_name, strategy_name, title, y_label, path, band=None):
    """A reference series and a strategy series on one axis."""
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(reference.index, reference.values, color=ORANGE, linewidth=2, label=reference_name)
    ax.plot(strategy.index, strategy.values, color=BLUE, linewidth=2, label=strategy_name)
    if band:
        start, end, text = band
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color=TEXT_2, alpha=0.10, linewidth=0)
        ax.annotate(text, xy=(pd.Timestamp(start), ax.get_ylim()[1] * 0.90), xytext=(-8, 0),
                    textcoords="offset points", ha="right", va="top", color=TEXT_2, fontsize=10)
    for series, name in ((reference, reference_name), (strategy, strategy_name)):
        ax.annotate(f"{name}: {series.iloc[-1]:,.0f}", xy=(series.index[-1], series.iloc[-1]),
                    xytext=(8, 0), textcoords="offset points", va="center", color=TEXT, fontsize=10)
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.grid(axis="x", visible=False)
    ax.margins(x=0.01)
    ax.legend(frameon=False, loc="upper left")
    fig.subplots_adjust(right=0.80)
    fig.tight_layout(rect=(0, 0, 0.84, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def bars(labels, values, title, y_label, path, horizontal=False, reference=None):
    """One series of bars, with a value label on each bar."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    if horizontal:
        rects = ax.barh(labels[::-1], values[::-1], color=BLUE, height=0.55)
        ax.bar_label(rects, labels=[f"{v:,.0f}" for v in values[::-1]], padding=4, color=TEXT, fontsize=10)
        ax.set_xlabel(y_label)
        ax.grid(axis="y", visible=False)
        if reference:
            ax.axvline(reference[0], color=ORANGE, linewidth=2)
            ax.annotate(f"{reference[1]}: {reference[0]:,.0f}", xy=(reference[0], 1.0),
                        xycoords=("data", "axes fraction"), xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", color=TEXT, fontsize=10)
        ax.set_title(title, pad=22)
        ax.margins(x=0.10)
    else:
        rects = ax.bar(labels, values, color=BLUE, width=0.55)
        ax.bar_label(rects, labels=[f"{v:,.0f}" for v in values], padding=3, color=TEXT, fontsize=10)
        ax.set_ylabel(y_label)
        ax.grid(axis="x", visible=False)
        ax.set_title(title)
        ax.margins(y=0.12)
    _save(fig, path)


def histogram(values, title, x_label, path, markers=None, marker_label="", bins=50):
    """Distribution of one number. `markers` is a list of (x, text) for marked cases."""
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.hist(values, bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=0.8, label="Random portfolios")
    ax.axvline(0, color=TEXT_2, linewidth=1.2)
    for k, (x, _) in enumerate(markers or []):
        ax.axvline(x, color=ORANGE, linewidth=2, label=marker_label if k == 0 else None)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Number of cases")
    ax.grid(axis="x", visible=False)
    if markers:
        ax.legend(frameon=False, loc="upper left")
    _save(fig, path)


def scatter(x, y, title, x_label, y_label, path):
    """One point for each case."""
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.scatter(x, y, s=10, color=BLUE, alpha=0.25, linewidths=0)
    ax.axhline(0, color=TEXT_2, linewidth=1.2)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    _save(fig, path)
