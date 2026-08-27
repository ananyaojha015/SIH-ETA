
import numpy as np
import pandas as pd

np.random.seed(7)

INPUT_FILE = "raw_journeys.csv"
OUTPUT_FILE = "raw_journeys_messy.csv"


def inject_missing_values(df, cols, frac=0.03):
    df = df.copy()
    for col in cols:
        mask = np.random.rand(len(df)) < frac
        df.loc[mask, col] = np.nan
    return df


def inject_outliers(df, col, frac=0.005, multiplier_range=(4, 8)):
    df = df.copy()
    mask = np.random.rand(len(df)) < frac
    multiplier = np.random.uniform(*multiplier_range, size=mask.sum())
    df.loc[mask, col] = df.loc[mask, col].abs() * multiplier + 50
    return df


def inject_duplicate_rows(df, frac=0.01):
    n_dupes = int(len(df) * frac)
    dupes = df.sample(n_dupes, random_state=1)
    return pd.concat([df, dupes], ignore_index=True)


def inject_bad_categoricals(df, col, frac=0.01):
    df = df.copy()
    mask = np.random.rand(len(df)) < frac
    bad_values = ["UNKNOWN", "N/A", "", "???"]
    df.loc[mask, col] = np.random.choice(bad_values, size=mask.sum())
    return df


def inject_negative_where_impossible(df, col, frac=0.005):
    """e.g. dwell_time_min should never be negative in reality — sensor glitch."""
    df = df.copy()
    mask = np.random.rand(len(df)) < frac
    df.loc[mask, col] = -df.loc[mask, col].abs()
    return df


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} clean rows")

    # 1. Missing values in a few realistic columns (sensor dropout, unreported weather)
    df = inject_missing_values(df, ["temperature_c", "visibility_km", "congestion_level"], frac=0.04)
    df = inject_missing_values(df, ["current_delay_min"], frac=0.01)

    # 2. Outliers (GPS glitch / bad sensor reading causing absurd delay values)
    df = inject_outliers(df, "current_delay_min", frac=0.004)
    df = inject_outliers(df, "actual_section_min", frac=0.003)

    # 3. Duplicate rows (common in real event-logging pipelines)
    df = inject_duplicate_rows(df, frac=0.01)

    # 4. Bad/placeholder categorical entries
    df = inject_bad_categoricals(df, "station_name", frac=0.01)

    # 5. Physically impossible negative values (sensor glitch)
    df = inject_negative_where_impossible(df, "dwell_time_min", frac=0.005)

    # 6. Shuffle so duplicates aren't neatly at the end
    df = df.sample(frac=1.0, random_state=3).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df):,} rows (with injected issues) -> {OUTPUT_FILE}")
    print(f"\nMissing value counts:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
