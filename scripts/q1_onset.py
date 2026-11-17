"""Question 1, second part: when did the number of days below the threshold start to climb?

Run from the repository root, after scripts/q1_days_below.py:
    python scripts/q1_onset.py

Writes:
    data/processed/q1_onset.csv   one row per threshold choice (see step 4)
    visuals/q1_onset.png          the yearly counts with the two fitted models

Steps (each one prints its numbers):
 1. Trend: fit a straight line to the yearly counts. A permutation test says how
    often a slope this steep appears by chance if the years are shuffled.
 2. Start year: compare two models with BIC (lower BIC = better; BIC punishes the
    extra parameter, so the break model must fit clearly better to win):
        line        days = a + b * year                       (rising the whole time)
        flat-rise   days = a + b * max(year - start, 0)       (flat until "start", then rising)
    For flat-rise we try every start year from 1982 to 2020 and keep the best one.
 3. Detection check: we build fake series that really are flat until 1990, 1995 or
    2000 and then rise, add noise of the same size as in the real data, and see how
    often step 2 finds the break. This tells us whether a late start would be visible.
 4. Threshold check: repeat steps 1-2 with the threshold taken from 1979-1988,
    1980-1989 and 1981-1990 September averages.
 5. Same comparison on the September extent itself (a continuous value, so it has no
    "zero days" floor like the counts have).
 6. Time of emergence: first year in which the fitted line is more than 1 or 2
    noise standard deviations above its value in the middle of the threshold decade.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from q1_days_below import count_days_below, load_filled_daily

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
VISUALS = ROOT / "visuals"

START_YEARS = range(1982, 2021)       # candidate start years for the flat-rise model
BASELINES = [(1979, 1988), (1980, 1989), (1981, 1990)]
MAIN_BASELINE = (1980, 1989)          # the one used in q1_days_below.py
rng = np.random.default_rng(seed=421)  # fixed seed so every run gives the same numbers


# ---------- small helpers ----------

def fit(design, y):
    """Least-squares fit. Returns (sum of squared errors, coefficients)."""
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    errors = y - design @ coefficients
    return (errors ** 2).sum(), coefficients


def bic(sse, n_params, n):
    """Bayesian information criterion for a least-squares fit. Lower is better."""
    return n * np.log(sse / n) + n_params * np.log(n)


def fit_line(years, y):
    design = np.column_stack([np.ones(len(years)), years])
    sse, (a, b) = fit(design, y)
    return sse, a, b


def fit_flat_rise(years, y):
    """Try every start year; return the best (sse, start, a, b)."""
    best = None
    for start in START_YEARS:
        design = np.column_stack([np.ones(len(years)), np.maximum(years - start, 0)])
        sse, (a, b) = fit(design, y)
        if best is None or sse < best[0]:
            best = (sse, start, a, b)
    return best


def compare_models(years, y):
    """Fit both models and return their BIC values and the best start year."""
    n = len(y)
    sse_line, a, b = fit_line(years, y)
    sse_flat, start, _, _ = fit_flat_rise(years, y)
    return {
        "slope_per_decade": 10 * b,
        "bic_line": bic(sse_line, 2, n),
        "bic_flat_rise": bic(sse_flat, 3, n),   # 3 parameters: a, b and the start year
        "best_start_year": start,
        "noise_sd": np.sqrt(sse_line / (n - 2)),
        "intercept": a,
        "slope": b,
    }


def permutation_p_value(years, y, n_shuffles=10000):
    """Share of shuffles whose slope is at least as large as the real one."""
    _, _, real_slope = fit_line(years, y)
    larger = 0
    for _ in range(n_shuffles):
        _, _, slope = fit_line(years, rng.permutation(y))
        if slope >= real_slope:
            larger += 1
    return (larger + 1) / (n_shuffles + 1)


def emergence_year(years, intercept, slope, noise_sd, baseline, k):
    """First year the fitted line is k noise-SDs above its value at the baseline middle."""
    middle = (baseline[0] + baseline[1]) / 2
    line_at_middle = intercept + slope * middle
    for year in years:
        if intercept + slope * year - line_at_middle >= k * noise_sd:
            return int(year)
    return None


def threshold_for(monthly, baseline):
    september = monthly[(monthly["month"] == 9)
                        & (monthly["year"] >= baseline[0])
                        & (monthly["year"] <= baseline[1])]
    return september["ice_extent"].mean()


# ---------- main ----------

def main():
    monthly = pd.read_csv(PROCESSED / "ice_monthly.csv")
    yearly = pd.read_csv(PROCESSED / "yearly.csv")
    filled = load_filled_daily()

    # Step 4 loops over the threshold choices; steps 1, 2 and 6 are done inside it.
    rows = []
    for baseline in BASELINES:
        threshold = threshold_for(monthly, baseline)
        counts = count_days_below(filled, threshold)
        years = counts["year"].to_numpy(dtype=float)
        days = counts["days_below"].to_numpy(dtype=float)

        result = compare_models(years, days)
        result["baseline"] = f"{baseline[0]}-{baseline[1]}"
        result["threshold"] = threshold
        result["p_value_trend"] = permutation_p_value(years, days)
        for k in (1, 2):
            result[f"emergence_{k}sd"] = emergence_year(
                years, result["intercept"], result["slope"], result["noise_sd"], baseline, k)
        rows.append(result)

        if baseline == MAIN_BASELINE:
            main_years, main_days, main_result = years, days, result

    table = pd.DataFrame(rows)[["baseline", "threshold", "slope_per_decade", "p_value_trend",
                                "bic_line", "bic_flat_rise", "best_start_year",
                                "noise_sd", "emergence_1sd", "emergence_2sd"]]
    table.to_csv(PROCESSED / "q1_onset.csv", index=False, float_format="%.4f")

    print("Steps 1, 2, 4, 6 - one row per threshold choice:")
    print(table.round(4).to_string(index=False))
    print("(p_value_trend 0.0001 is the smallest possible with 10000 shuffles: "
          "no shuffle gave a slope as steep as the real one)")

    # Step 3: would a late start be found?
    print("\nStep 3 - detection check (1000 fake series each, noise SD "
          f"{main_result['noise_sd']:.1f} days):")
    n = len(main_years)
    for true_start in (1990, 1995, 2000):
        # slope chosen so the fake series ends near the real 2025 level (~95 days)
        slope = (95 - 20) / (2025 - true_start)
        found = 0
        found_years = []
        for _ in range(1000):
            fake = 20 + slope * np.maximum(main_years - true_start, 0) + rng.normal(0, main_result["noise_sd"], n)
            check = compare_models(main_years, fake)
            if check["bic_flat_rise"] < check["bic_line"]:
                found += 1
            found_years.append(check["best_start_year"])
        low, high = np.percentile(found_years, [5, 95])
        print(f"  true start {true_start}: flat-rise model wins in {found / 10:.0f}% "
              f"of series; estimated start (5-95%) {low:.0f}-{high:.0f}")

    # Step 5: the same comparison on September extent
    sept_years = yearly["year"].to_numpy(dtype=float)
    sept_extent = -yearly["september_ice_extent"].to_numpy()  # minus sign: "rising" = losing ice
    sept = compare_models(sept_years, sept_extent)
    print("\nStep 5 - September extent (million km², sign flipped so loss = rise):")
    print(f"  loss per decade {sept['slope_per_decade']:.3f}, "
          f"BIC line {sept['bic_line']:.1f}, BIC flat-rise {sept['bic_flat_rise']:.1f} "
          f"(best start {sept['best_start_year']})")

    plot(main_years, main_days, main_result)


def plot(years, days, result):
    _, start, a_flat, b_flat = fit_flat_rise(years, days)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(years, days, color="#4a90c2", label="Days below threshold")
    ax.plot(years, result["intercept"] + result["slope"] * years, color="black",
            linewidth=2, label=f"Straight line (BIC {result['bic_line']:.1f})")
    ax.plot(years, a_flat + b_flat * np.maximum(years - start, 0), color="#d9534f",
            linestyle="--", linewidth=2,
            label=f"Best flat-then-rise, start {start} (BIC {result['bic_flat_rise']:.1f})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Days per year")
    ax.set_title("Days below the 1980s September average: straight line vs. flat-then-rise")
    ax.legend()
    fig.tight_layout()
    fig.savefig(VISUALS / "q1_onset.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
