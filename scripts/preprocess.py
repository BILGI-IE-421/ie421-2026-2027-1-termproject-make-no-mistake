"""Clean the raw files and build the tables we analyse.

Run from the repository root, after scripts/download_data.py:
    python scripts/preprocess.py

Reads data/raw/ and writes four files to data/processed/:
    ice_daily.csv       one row per day:   date, year, month, day, extent
    ice_monthly.csv     one row per month: mean extent and how many days it is based on
    monthly_joined.csv  ice + temperature + CO2 joined on year and month (1979 onwards)
    yearly.csv          one row per complete year, the values our three questions need
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

FIRST_YEAR = 1979  # first full year of sea-ice data; all three sources overlap from here
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_ice_daily():
    """NSIDC daily sea-ice extent (million km²)."""
    # Row 2 of the file holds units (YYYY, MM, ...), not data, so we skip it.
    # skipinitialspace removes the spaces in front of the column names and values.
    ice = pd.read_csv(RAW / "nsidc_arctic_daily_extent.csv",
                      skiprows=[1], skipinitialspace=True)
    ice = ice[["Year", "Month", "Day", "Extent"]]
    ice.columns = ["year", "month", "day", "extent"]
    ice["date"] = pd.to_datetime(ice[["year", "month", "day"]])
    return ice[["date", "year", "month", "day", "extent"]]


def make_ice_monthly(ice_daily):
    """Average the daily values of each month.

    n_days says how many daily values went into the average. Before mid-1987 there
    is a value only every other day, and December 1987 has almost no data.
    """
    monthly = ice_daily.groupby(["year", "month"]).agg(
        ice_extent=("extent", "mean"),
        n_days=("extent", "count"),
    )
    return monthly.reset_index()


def load_gistemp(file_name, column_name):
    """NASA GISTEMP: one row per year, one column per month -> one row per month."""
    # Row 1 is a title line. "***" marks a month that has no value yet.
    wide = pd.read_csv(RAW / file_name, skiprows=1, na_values="***")
    wide = wide[["Year"] + MONTH_NAMES]
    long = wide.melt(id_vars="Year", var_name="month_name", value_name=column_name)
    long["month"] = long["month_name"].apply(lambda name: MONTH_NAMES.index(name) + 1)
    long = long.rename(columns={"Year": "year"})
    return long[["year", "month", column_name]].dropna()


def load_co2():
    """NOAA Mauna Loa monthly mean CO2 (ppm). Lines starting with # are notes."""
    co2 = pd.read_csv(RAW / "noaa_co2_monthly.csv", comment="#")
    co2 = co2[["year", "month", "average"]]
    return co2.rename(columns={"average": "co2_ppm"})


def make_yearly(monthly):
    """One row per year with the values our three questions use.

    Only years with all 12 months present are kept (so the current, unfinished
    year is left out).
    """
    rows = []
    for year, months in monthly.groupby("year"):
        if len(months) < 12:
            continue
        september = months[months["month"] == 9]
        spring = months[months["month"].isin([3, 4, 5])]  # March, April, May
        rows.append({
            "year": year,
            "september_ice_extent": september["ice_extent"].iloc[0],
            "march_ice_extent": months[months["month"] == 3]["ice_extent"].iloc[0],
            "nh_spring_anomaly": spring["nh_anomaly"].mean(),
            "nh_annual_anomaly": months["nh_anomaly"].mean(),
            "global_annual_anomaly": months["global_anomaly"].mean(),
            "co2_annual_mean": months["co2_ppm"].mean(),
        })
    return pd.DataFrame(rows)


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)

    ice_daily = load_ice_daily()
    ice_monthly = make_ice_monthly(ice_daily)
    nh = load_gistemp("gistemp_nh_monthly.csv", "nh_anomaly")
    glob = load_gistemp("gistemp_global_monthly.csv", "global_anomaly")
    co2 = load_co2()

    # Join on year and month. "inner" keeps only months that exist in every source.
    monthly = ice_monthly.merge(nh, on=["year", "month"], how="inner")
    monthly = monthly.merge(glob, on=["year", "month"], how="inner")
    monthly = monthly.merge(co2, on=["year", "month"], how="inner")
    monthly = monthly[monthly["year"] >= FIRST_YEAR]

    yearly = make_yearly(monthly)

    ice_daily.to_csv(PROCESSED / "ice_daily.csv", index=False)
    ice_monthly.to_csv(PROCESSED / "ice_monthly.csv", index=False, float_format="%.3f")
    monthly.to_csv(PROCESSED / "monthly_joined.csv", index=False, float_format="%.3f")
    yearly.to_csv(PROCESSED / "yearly.csv", index=False, float_format="%.3f")

    print(f"ice_daily.csv      {len(ice_daily)} rows")
    print(f"ice_monthly.csv    {len(ice_monthly)} rows")
    print(f"monthly_joined.csv {len(monthly)} rows "
          f"({monthly['year'].min()}-{monthly['month'].iloc[0]:02d} to "
          f"{monthly['year'].max()}-{monthly['month'].iloc[-1]:02d})")
    print(f"yearly.csv         {len(yearly)} rows "
          f"({yearly['year'].min()} to {yearly['year'].max()})")


if __name__ == "__main__":
    main()
