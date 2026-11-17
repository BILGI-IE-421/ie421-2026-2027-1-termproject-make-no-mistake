"""Make the figures shown on the website (index.html).

Run from the repository root, after scripts/preprocess.py and scripts/q1_days_below.py:
    python scripts/figures.py

Writes to visuals/:
    fig1_days_below.png      trend over time: days per year below the 1980s September average
    fig2_monthly_loss.png    comparison across categories: ice in each month, 1980s vs 2010s

Rules we follow for every figure: a title that states the finding, labels with units,
bars that start at zero, a colour-blind-safe palette and a source caption.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
VISUALS = ROOT / "visuals"

# Colour-blind-safe colours (seaborn "colorblind" palette)
BLUE = "#0173b2"
ORANGE = "#de8f05"
SOURCE_ICE = "Source: NSIDC Sea Ice Index G02135 v4 (daily Arctic sea-ice extent). Figure: team make-no-mistake."
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def add_source(fig, text):
    fig.text(0.01, 0.01, text, fontsize=8, color="gray")


def figure_1_days_below():
    table = pd.read_csv(PROCESSED / "q1_days_below.csv")
    years = table["year"]
    days = table["days_below"]

    # Straight-line trend (q1_onset.py shows a straight line fits better than a late start)
    slope, intercept = np.polyfit(years, days, 1)
    early = days[years <= 1988].mean()
    recent = days[years >= 2016].mean()

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(years, days, color=BLUE, label="Days below the threshold")
    ax.plot(years, intercept + slope * years, color=ORANGE, linewidth=2.5,
            label=f"Straight-line trend: +{10 * slope:.0f} days per decade")
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("Days per year")
    ax.set_title("Arctic sea ice now spends about three months a year below its 1980s September level",
                 fontsize=12, loc="left")
    ax.text(1979, 112, f"1979-1988 average: {early:.0f} days     2016-2025 average: {recent:.0f} days",
            fontsize=10)
    ax.set_ylim(0, 120)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 0.93))
    fig.subplots_adjust(bottom=0.15)
    add_source(fig, SOURCE_ICE + " Threshold: mean September extent 1980-1989 = 7.21 million km².")
    fig.savefig(VISUALS / "fig1_days_below.png", dpi=150)
    plt.close(fig)


def figure_2_monthly_loss():
    monthly = pd.read_csv(PROCESSED / "monthly_joined.csv")
    eighties = monthly[(monthly["year"] >= 1980) & (monthly["year"] <= 1989)]
    tens = monthly[(monthly["year"] >= 2010) & (monthly["year"] <= 2019)]
    mean_80s = eighties.groupby("month")["ice_extent"].mean()
    mean_10s = tens.groupby("month")["ice_extent"].mean()
    loss_percent = 100 * (mean_80s - mean_10s) / mean_80s

    x = np.arange(12)
    width = 0.4
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x - width / 2, mean_80s.values, width, color=BLUE, label="1980s average")
    ax.bar(x + width / 2, mean_10s.values, width, color=ORANGE, label="2010s average")
    # Write the percentage lost above each pair of bars
    for i in range(12):
        ax.text(x[i], mean_80s.values[i] + 0.3, f"-{loss_percent.values[i]:.0f}%",
                ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS)
    ax.set_ylim(0, 18)
    ax.set_xlabel("Month")
    ax.set_ylabel("Mean sea-ice extent (million km²)")
    ax.set_title(f"September lost a third of its ice since the 1980s; March lost only "
                 f"{loss_percent[3]:.0f}%", fontsize=12, loc="left")
    ax.legend(loc="upper center", ncol=2)
    fig.subplots_adjust(bottom=0.15)
    add_source(fig, SOURCE_ICE + " Percent = loss from the 1980s to the 2010s.")
    fig.savefig(VISUALS / "fig2_monthly_loss.png", dpi=150)
    plt.close(fig)


def main():
    VISUALS.mkdir(exist_ok=True)
    figure_1_days_below()
    figure_2_monthly_loss()
    print("Saved visuals/fig1_days_below.png and visuals/fig2_monthly_loss.png")


if __name__ == "__main__":
    main()
