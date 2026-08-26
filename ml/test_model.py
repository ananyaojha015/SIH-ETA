import pandas as pd
import joblib

# Load trained model
model = joblib.load("eta_model.joblib")

# Load dataset
df = pd.read_excel("features_ml_ready.xlsx")

# Convert date and create the same features used during training
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.month
df["day_of_month"] = df["date"].dt.day

# Features must match train_model.py
features = [
    "station_seq",
    "cum_distance_km",
    "distance_to_next_km",
    "distance_to_destination_km",
    "journey_progress_frac",
    "hour_of_day",
    "day_of_week",
    "is_peak_hour",
    "is_weekend",
    "current_delay_min",
    "delay_trend",
    "dwell_time_min",
    "sched_section_min",
    "actual_section_min",
    "section_delay_delta_min",
    "congestion_level",
    "is_rain",
    "is_fog",
    "temperature_c",
    "visibility_km",
    "weather_severity",
    "train_sched_avg_speed_kmph",
    "train_congestion_sensitivity_meta",
    "train_recovery_rate_meta",
    "train_avg_delay",
    "train_delay_std",
    "station_avg_dwell",
    "month",
    "day_of_month",
    "station_id",
    "station_name"
]

# Pick one example row
sample = df.iloc[[0]]

X = sample[features]

# Predict
prediction = model.predict(X)[0]

print("=" * 60)
print("ETA MODEL TEST")
print("=" * 60)

print("Train ID:", sample["train_id"].iloc[0])
print("Station:", sample["station_name"].iloc[0])
print("Current delay:", sample["current_delay_min"].iloc[0], "minutes")

print()
print("Actual final delay:",
      sample["target_final_delay_min"].iloc[0], "minutes")

print("Predicted final delay:",
      round(prediction, 2), "minutes")

print()
print("Prediction error:",
      round(
          sample["target_final_delay_min"].iloc[0] - prediction,
          2
      ),
      "minutes")