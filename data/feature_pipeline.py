
import numpy as np
import pandas as pd

RAW_FILE = "raw_journeys_messy.csv"
STATIONS_FILE = "stations.csv"
TRAINS_FILE = "trains_meta.csv"
OUTPUT_FILE = "features_ml_ready.csv"


# -----------------------------------------------------------------------
# STEP 1 — LOAD
# -----------------------------------------------------------------------
def load_data():
    df = pd.read_csv(RAW_FILE)
    stations = pd.read_csv(STATIONS_FILE)
    trains = pd.read_csv(TRAINS_FILE)
    return df, stations, trains


# -----------------------------------------------------------------------
# STEP 2 — CLEANING
# -----------------------------------------------------------------------
def clean_data(df, stations):
    log = []
    n0 = len(df)

    # 2.1 Drop exact duplicate rows
    before = len(df)
    df = df.drop_duplicates().copy()  # .copy() avoids pandas SettingWithCopyWarning below
    log.append(f"Dropped {before - len(df)} exact duplicate rows")

    # 2.2 Fix bad categorical placeholders in station_name using station_id (which is reliable)
    bad_vals = {"UNKNOWN", "N/A", "", "???"}
    mask_bad_name = df["station_name"].isin(bad_vals) | df["station_name"].isna()
    id_to_name = stations.set_index("station_id")["station_name"].to_dict()
    df.loc[mask_bad_name, "station_name"] = df.loc[mask_bad_name, "station_id"].map(id_to_name)
    log.append(f"Repaired {mask_bad_name.sum()} bad station_name values using station_id lookup")

    # 2.3 Fix physically impossible negative dwell time -> take absolute value
    neg_dwell = df["dwell_time_min"] < 0
    df.loc[neg_dwell, "dwell_time_min"] = df.loc[neg_dwell, "dwell_time_min"].abs()
    log.append(f"Fixed {neg_dwell.sum()} negative dwell_time_min values (sensor glitch)")

    # 2.4 Cap outliers using IQR method on delay & section time columns
    for col in ["current_delay_min", "actual_section_min"]:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        upper = q3 + 3 * iqr
        lower = q1 - 3 * iqr
        n_outliers = ((df[col] > upper) | (df[col] < lower)).sum()
        df[col] = df[col].clip(lower=lower, upper=upper)
        log.append(f"Capped {n_outliers} outliers in '{col}' to [{lower:.1f}, {upper:.1f}]")

    # 2.5 Impute missing numeric values
    # - congestion_level, temperature_c, visibility_km: fill with station+hour median
    for col in ["congestion_level", "temperature_c", "visibility_km"]:
        n_missing = df[col].isna().sum()
        df[col] = df.groupby("hour_of_day")[col].transform(lambda s: s.fillna(s.median()))
        df[col] = df[col].fillna(df[col].median())  # fallback for any remaining
        log.append(f"Imputed {n_missing} missing '{col}' values using hour-of-day median")

    # - current_delay_min: fill with per-train median delay (train behaviour is a good prior)
    n_missing_delay = df["current_delay_min"].isna().sum()
    df["current_delay_min"] = df.groupby("train_id")["current_delay_min"].transform(
        lambda s: s.fillna(s.median())
    )
    df["current_delay_min"] = df["current_delay_min"].fillna(df["current_delay_min"].median())
    log.append(f"Imputed {n_missing_delay} missing 'current_delay_min' values using per-train median")

    # 2.6 Recompute distance/sched fields for last-station rows (legitimately NaN, not messy)
    # These stay NaN — they represent "no next section" at the destination, which is valid.

    print("\n".join(log))
    print(f"\nCleaning complete: {n0} -> {len(df)} rows")
    return df


# -----------------------------------------------------------------------
# STEP 3 — FEATURE ENGINEERING
# -----------------------------------------------------------------------
def engineer_features(df, stations, trains):
    df = df.sort_values(["train_id", "date", "station_seq"]).reset_index(drop=True)
    n_stations = stations["station_seq"].max() + 1

    # 3.1 Distance to destination
    total_distance = stations["cum_distance_km"].max()
    df["distance_to_destination_km"] = total_distance - df["cum_distance_km"]

    # 3.2 Progress fraction of journey completed (0 = origin, 1 = destination)
    df["journey_progress_frac"] = df["cum_distance_km"] / total_distance

    # 3.3 Section delay delta (how much delay changed on the last section) — key ML signal
    df["section_delay_delta_min"] = df["actual_section_min"] - df["sched_section_min"]

    # 3.4 Rolling delay trend per train per day (is delay increasing or decreasing?)
    df["delay_trend"] = (
        df.groupby(["train_id", "date"])["current_delay_min"]
        .diff()
        .fillna(0)
    )

    # 3.5 Train behaviour fingerprint (historical aggregates, joined from trains_meta
    #     + computed empirical stats across the whole dataset — this is what lets the
    #     model learn "this train usually recovers delay after station X")
    train_stats = (
        df.groupby("train_id")["current_delay_min"]
        .agg(train_avg_delay="mean", train_delay_std="std")
        .reset_index()
    )
    df = df.merge(train_stats, on="train_id", how="left")
    df = df.merge(
        trains[["train_id", "avg_speed_kmph", "congestion_sensitivity", "recovery_rate"]]
        .rename(columns={
            "avg_speed_kmph": "train_sched_avg_speed_kmph",
            "congestion_sensitivity": "train_congestion_sensitivity_meta",
            "recovery_rate": "train_recovery_rate_meta",
        }),
        on="train_id", how="left",
    )

    # 3.6 Station-level historical dwell/delay stats (does this station chronically cause delay?)
    station_stats = (
        df.groupby("station_id")["dwell_time_min"]
        .agg(station_avg_dwell="mean")
        .reset_index()
    )
    df = df.merge(station_stats, on="station_id", how="left")

    # 3.7 Peak hour flag + weekend flag (cheap but useful signals)
    df["is_peak_hour"] = df["hour_of_day"].isin([7, 8, 9, 17, 18, 19, 20]).astype(int)
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # 3.8 Weather severity score (single combined feature, sometimes easier for tree models)
    df["weather_severity"] = (
        df["is_rain"] * 1.0 + df["is_fog"] * 1.5 + (df["visibility_km"] < 2).astype(int) * 1.0
    )

    # 3.9 TARGET VARIABLE — the label Anubha's model will predict:
    #     the FINAL delay this train ends up with at its destination for this run.
    final_delay = (
        df[df["distance_to_destination_km"] == 0]
        .groupby(["train_id", "date"])["current_delay_min"]
        .first()
        .rename("target_final_delay_min")
    )
    df = df.merge(final_delay, on=["train_id", "date"], how="left")

    # Also a simpler next-station-only target, useful for a first baseline model
    df["target_next_station_delay_min"] = (
        df.groupby(["train_id", "date"])["current_delay_min"].shift(-1)
    )

    return df


# -----------------------------------------------------------------------
# STEP 4 — FINAL SELECTION / ORDERING FOR ML
# -----------------------------------------------------------------------
def select_ml_columns(df):
    cols = [
        # identifiers (keep for traceability, drop before training if needed)
        "date", "train_id", "station_id", "station_name", "station_seq",
        # core numeric features
        "cum_distance_km", "distance_to_next_km", "distance_to_destination_km",
        "journey_progress_frac", "hour_of_day", "day_of_week", "is_peak_hour", "is_weekend",
        "current_delay_min", "delay_trend", "dwell_time_min",
        "sched_section_min", "actual_section_min", "section_delay_delta_min",
        "congestion_level",
        "is_rain", "is_fog", "temperature_c", "visibility_km", "weather_severity",
        "train_sched_avg_speed_kmph", "train_congestion_sensitivity_meta",
        "train_recovery_rate_meta", "train_avg_delay", "train_delay_std",
        "station_avg_dwell",
        # targets
        "target_next_station_delay_min", "target_final_delay_min",
    ]
    return df[[c for c in cols if c in df.columns]]


# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------
if __name__ == "__main__":
    df, stations, trains = load_data()
    print(f"Loaded raw data: {len(df):,} rows\n")

    print("=" * 60)
    print("CLEANING")
    print("=" * 60)
    df_clean = clean_data(df, stations)

    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)
    df_feat = engineer_features(df_clean, stations, trains)

    df_final = select_ml_columns(df_feat)
    df_final.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved ML-ready dataset -> {OUTPUT_FILE}")
    print(f"Shape: {df_final.shape}")
    print(f"\nColumns:\n{list(df_final.columns)}")
    print(f"\nRemaining nulls per column:\n{df_final.isnull().sum()[df_final.isnull().sum() > 0]}")
    print(f"\nSample rows:\n{df_final.head(5).to_string()}")