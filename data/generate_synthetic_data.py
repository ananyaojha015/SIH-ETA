

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------
SEED = 42
np.random.seed(SEED)

N_STATIONS = 12
N_TRAINS = 25
N_DAYS = 60          # simulate 60 days of running -> plenty of rows
START_DATE = datetime(2026, 6, 1)

OUTPUT_FILE = "raw_journeys.csv"

# -----------------------------------------------------------------------
# 1. BUILD THE ROUTE / STATION NETWORK
# -----------------------------------------------------------------------
def build_stations(n_stations=N_STATIONS):
    """Create a single linear trunk route with cumulative distance."""
    station_names = [
        "Delhi", "Mathura", "Agra", "Gwalior", "Jhansi", "Bhopal",
        "Itarsi", "Nagpur", "Raipur", "Sambalpur", "Cuttack", "Bhubaneswar",
        "Kharagpur", "Kanpur", "Allahabad"
    ][:n_stations]

    # Section lengths (km) between consecutive stations — some short, some long
    section_km = np.random.randint(45, 220, size=n_stations - 1)
    cum_dist = np.concatenate([[0], np.cumsum(section_km)])

    stations = pd.DataFrame({
        "station_seq": np.arange(n_stations),
        "station_id": [f"S{idx+1:02d}" for idx in range(n_stations)],
        "station_name": station_names,
        "cum_distance_km": cum_dist,
    })
    stations["section_km_to_next"] = list(section_km) + [np.nan]
    return stations


def build_trains(stations, n_trains=N_TRAINS):
    """Assign each train a schedule (scheduled time at every station) and
    an inherent 'behaviour profile' that biases its delays consistently."""
    trains = []
    for i in range(n_trains):
        train_id = f"1{2000 + i}"  # looks like an Indian train number
        avg_speed_kmph = np.random.uniform(45, 90)     # scheduled avg speed
        base_dwell_min = np.random.uniform(2, 6)        # baseline stop time
        punctuality_bias = np.random.normal(0, 4)       # some trains chronically late/early
        congestion_sensitivity = np.random.uniform(0.3, 1.5)  # how much congestion hurts this train
        recovery_rate = np.random.uniform(0.20, 0.50)    # fraction of delay recovered per section

        # Departure time from origin station, spread across the day
        origin_dep_minutes = np.random.randint(0, 24 * 60)

        trains.append({
            "train_id": train_id,
            "avg_speed_kmph": avg_speed_kmph,
            "base_dwell_min": base_dwell_min,
            "punctuality_bias": punctuality_bias,
            "congestion_sensitivity": congestion_sensitivity,
            "recovery_rate": recovery_rate,
            "origin_dep_minutes": origin_dep_minutes,
        })
    return pd.DataFrame(trains)


# -----------------------------------------------------------------------
# 2. SIMULATE EXTERNAL CONDITIONS
# -----------------------------------------------------------------------
def simulate_weather(date):
    """Very simple seasonal weather model for India (monsoon-heavy)."""
    month = date.month
    if month in (6, 7, 8, 9):          # monsoon
        rain_prob = 0.45
    elif month in (12, 1):             # winter fog belt
        rain_prob = 0.05
    else:
        rain_prob = 0.15

    is_rain = np.random.rand() < rain_prob
    is_fog = (month in (12, 1)) and (np.random.rand() < 0.3)
    temperature_c = np.random.normal(28, 6)
    visibility_km = np.random.uniform(0.5, 2.0) if is_fog else np.random.uniform(3, 10)

    return {
        "is_rain": int(is_rain),
        "is_fog": int(is_fog),
        "temperature_c": round(temperature_c, 1),
        "visibility_km": round(visibility_km, 2),
    }


def simulate_congestion(hour_of_day):
    """Peak-hour congestion proxy (0=empty, 1=heavily congested)."""
    if hour_of_day in (7, 8, 9, 17, 18, 19, 20):
        base = np.random.uniform(0.5, 1.0)
    elif hour_of_day in (10, 11, 16, 21):
        base = np.random.uniform(0.2, 0.6)
    else:
        base = np.random.uniform(0.0, 0.3)
    return round(min(base, 1.0), 3)


# -----------------------------------------------------------------------
# 3. SIMULATE JOURNEYS
# -----------------------------------------------------------------------
def simulate_journeys(stations, trains, n_days=N_DAYS, start_date=START_DATE):
    rows = []
    n_stations = len(stations)

    for day_offset in range(n_days):
        run_date = start_date + timedelta(days=day_offset)

        for _, train in trains.iterrows():
            cur_delay = 0.0  # minutes, accumulates/recovers across the journey
            sched_dep_time = run_date + timedelta(minutes=int(train["origin_dep_minutes"]))
            actual_time = sched_dep_time

            for seq in range(n_stations):
                st = stations.iloc[seq]
                hour = actual_time.hour
                weather = simulate_weather(actual_time)
                congestion = simulate_congestion(hour)

                # ---- Dwell time at this station ----
                if seq == 0:
                    dwell = 0.0  # origin: no arrival dwell
                elif seq == n_stations - 1:
                    dwell = 0.0  # destination: no departure dwell
                else:
                    dwell_noise = np.random.exponential(1.5)
                    congestion_dwell_extra = congestion * np.random.uniform(0, 3)
                    dwell = max(0, train["base_dwell_min"] + dwell_noise + congestion_dwell_extra)

                # ---- Section running time to next station ----
                if seq < n_stations - 1:
                    section_km = st["section_km_to_next"]
                    sched_section_min = (section_km / train["avg_speed_kmph"]) * 60

                    # Delay-inducing factors
                    weather_extra = 0.0
                    if weather["is_rain"]:
                        weather_extra += sched_section_min * np.random.uniform(0.02, 0.08)
                    if weather["is_fog"]:
                        weather_extra += sched_section_min * np.random.uniform(0.04, 0.12)

                    congestion_extra = (
                        sched_section_min * congestion * train["congestion_sensitivity"] * 0.10
                    )

                    random_noise = np.random.normal(0, sched_section_min * 0.04)

                    # Delay recovery: trains partially claw back existing delay,
                    # pulling cur_delay toward 0 from either side (never overshoots).
                    pull_frac = train["recovery_rate"] * np.random.uniform(0.8, 1.3)
                    pull_frac = min(pull_frac, 1.0)
                    recovery = -cur_delay * pull_frac

                    section_delay_delta = (
                        weather_extra + congestion_extra + random_noise
                        + recovery + train["punctuality_bias"] * 0.05
                    )
                    actual_section_min = max(1.0, sched_section_min + section_delay_delta)
                else:
                    sched_section_min = np.nan
                    actual_section_min = np.nan

                cur_delay = cur_delay + (actual_section_min - sched_section_min if seq < n_stations - 1 else 0)
                cur_delay = round(cur_delay, 2)

                sched_arrival = sched_dep_time + timedelta(
                    minutes=float(stations.iloc[:seq + 1]["section_km_to_next"].fillna(0).iloc[:-1].sum() * 0
                                   if seq == 0 else 0)
                )
                # (kept simple: compute scheduled cumulative time directly below instead)

                rows.append({
                    "date": run_date.date().isoformat(),
                    "train_id": train["train_id"],
                    "station_seq": seq,
                    "station_id": st["station_id"],
                    "station_name": st["station_name"],
                    "cum_distance_km": st["cum_distance_km"],
                    "distance_to_next_km": st["section_km_to_next"],
                    "hour_of_day": hour,
                    "day_of_week": actual_time.weekday(),
                    "current_delay_min": cur_delay,
                    "dwell_time_min": round(dwell, 2),
                    "sched_section_min": None if pd.isna(sched_section_min) else round(sched_section_min, 2),
                    "actual_section_min": None if pd.isna(actual_section_min) else round(actual_section_min, 2),
                    "congestion_level": congestion,
                    "is_rain": weather["is_rain"],
                    "is_fog": weather["is_fog"],
                    "temperature_c": weather["temperature_c"],
                    "visibility_km": weather["visibility_km"],
                    "avg_speed_kmph": round(train["avg_speed_kmph"], 1),
                    "train_congestion_sensitivity": round(train["congestion_sensitivity"], 3),
                    "train_recovery_rate": round(train["recovery_rate"], 3),
                })

                # advance actual_time for next station
                step_min = dwell + (actual_section_min if seq < n_stations - 1 else 0)
                actual_time = actual_time + timedelta(minutes=float(step_min))

    return pd.DataFrame(rows)


# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------
if __name__ == "__main__":
    stations = build_stations()
    trains = build_trains(stations)

    print(f"Simulating {N_TRAINS} trains x {N_DAYS} days x {N_STATIONS} stations...")
    journeys = simulate_journeys(stations, trains)

    journeys.to_csv(OUTPUT_FILE, index=False)
    stations.to_csv("stations.csv", index=False)
    trains.to_csv("trains_meta.csv", index=False)

    print(f"\nDone.")
    print(f" - {OUTPUT_FILE}: {len(journeys):,} rows")
    print(f" - stations.csv: {len(stations)} rows")
    print(f" - trains_meta.csv: {len(trains)} rows")
    print("\nSample:")
    print(journeys.head(10).to_string())
