"""Check the method of question 1: does filling missing days give the right count?

Run from the repository root, after scripts/preprocess.py:
    python scripts/q1_method_check.py

Idea: from 1990 on we have a value for every day, so we know the true count.
We delete every other day from those years (so they look like the 1979-1987 data),
count again with three methods, and compare with the true count:

    filled  fill each missing day from its neighbours, then count (what q1_days_below.py does)
    share   share of measured days below the threshold, times the number of days in the year
    raw     count the remaining days directly, no correction

Each year is tested twice: once deleting the even days, once deleting the odd days.
Writes data/processed/q1_method_check.csv and prints a summary.
"""

from pathlib import Path

import pandas as pd

from q1_days_below import september_1980s_average

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"


def main():
    threshold = september_1980s_average()
    daily = pd.read_csv(PROCESSED / "ice_daily.csv", parse_dates=["date"])
    extent = daily.set_index("date")["extent"].asfreq("D")

    rows = []
    for year in range(1990, 2026):
        one_year = extent[extent.index.year == year]
        if one_year.isna().any():
            continue  # only use years that have every day
        true_count = (one_year < threshold).sum()

        for start in (0, 1):  # 0: delete days 1, 3, 5 ...  1: delete days 2, 4, 6 ...
            thinned = one_year.copy()
            thinned.iloc[start::2] = float("nan")
            # The first or last day may be missing after thinning; fill it from its one neighbour.
            filled = thinned.interpolate().bfill().ffill()
            measured = thinned.dropna()

            rows.append({
                "year": year,
                "deleted": "odd days" if start == 0 else "even days",
                "true": true_count,
                "filled": (filled < threshold).sum(),
                "share": round((measured < threshold).mean() * len(one_year), 1),
                "raw": (measured < threshold).sum(),
            })

    table = pd.DataFrame(rows)
    table.to_csv(PROCESSED / "q1_method_check.csv", index=False)

    print(f"Tested {table['year'].nunique()} years, each twice ({len(table)} tests).")
    print("Error = method count minus true count (days per year)")
    for method in ["filled", "share", "raw"]:
        error = table[method] - table["true"]
        print(f"  {method:6s}  mean error {error.mean():+6.2f}   largest error {error.abs().max():5.1f}")

    # Second check, on the real every-other-day years 1979-1986:
    # do the "filled" and "share" methods agree with each other?
    q1 = pd.read_csv(PROCESSED / "q1_days_below.csv").set_index("year")
    print("\nReal data 1979-1986 (measured every other day):")
    print("  year  filled  share")
    for year in range(1979, 1987):
        measured = daily[daily["year"] == year]["extent"]
        days_in_year = 366 if year % 4 == 0 else 365
        share = (measured < threshold).mean() * days_in_year
        print(f"  {year}  {q1.loc[year, 'days_below']:6d}  {share:5.1f}")


if __name__ == "__main__":
    main()
