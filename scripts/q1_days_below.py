"""Question 1: how many days per year is Arctic sea ice below the 1980s September average?

Run from the repository root, after scripts/preprocess.py:
    python scripts/q1_days_below.py

Writes:
    data/processed/q1_days_below.csv   one row per year: days below the threshold
    visuals/q1_days_below.png          bar chart of those counts

Why we fill missing days:
    Until August 1987 the satellite measured the ice only every other day, so early
    years have about 183 values instead of 365. Counting them directly would show
    about half the real number of days. We fill each single missing day with the
    average of the day before and the day after (linear interpolation).
    The long gap from 3 Dec 1987 to 12 Jan 1988 is NOT filled; it is in winter,
    when the ice is far above the threshold, so it does not change the counts.
    scripts/q1_method_check.py tests this choice.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
VISUALS = ROOT / "visuals"

FIRST_YEAR = 1979
LAST_YEAR = 2025  # last complete year


def september_1980s_average():
    """Threshold: mean of the September monthly extents of 1980-1989 (million km²)."""
    monthly = pd.read_csv(PROCESSED / "ice_monthly.csv")
    september_1980s = monthly[(monthly["month"] == 9)
                              & (monthly["year"] >= 1980)
                              & (monthly["year"] <= 1989)]
    return september_1980s["ice_extent"].mean()


def load_filled_daily():
    """Daily extent with one row for every calendar day; single missing days filled."""
    daily = pd.read_csv(PROCESSED / "ice_daily.csv", parse_dates=["date"])
    extent = daily.set_index("date")["extent"]

    # One row for every day. Days with no measurement become NaN (empty).
    extent = extent.asfreq("D")

    # A missing day is "single" if both the day before and the day after have a value.
    missing = extent.isna()
    single_missing = missing & extent.shift(1).notna() & extent.shift(-1).notna()

    # Fill every gap by drawing a straight line between the known values ...
    filled = extent.interpolate()
    # ... but keep long gaps (two or more missing days in a row) empty.
    filled[missing & ~single_missing] = float("nan")
    return filled


def count_days_below(filled, threshold):
    """For each year: days below the threshold and days that still have no value."""
    rows = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        one_year = filled[filled.index.year == year]
        rows.append({
            "year": year,
            "days_below": int((one_year < threshold).sum()),
            "days_without_data": int(one_year.isna().sum()),
        })
    return pd.DataFrame(rows)


def plot(table, threshold):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(table["year"], table["days_below"], color="#4a90c2", label="Days below threshold")
    # 5-year moving average to show the general direction
    moving_average = table["days_below"].rolling(5, center=True).mean()
    ax.plot(table["year"], moving_average, color="black", linewidth=2,
            label="5-year moving average")
    ax.set_xlabel("Year")
    ax.set_ylabel("Days per year")
    ax.set_title(f"Days per year with Arctic sea-ice extent below the 1980s "
                 f"September average ({threshold:.2f} million km²)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(VISUALS / "q1_days_below.png", dpi=150)
    plt.close(fig)


def main():
    VISUALS.mkdir(exist_ok=True)
    threshold = september_1980s_average()
    filled = load_filled_daily()
    table = count_days_below(filled, threshold)

    table.to_csv(PROCESSED / "q1_days_below.csv", index=False)
    plot(table, threshold)

    print(f"Threshold (1980s September average): {threshold:.3f} million km²")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
