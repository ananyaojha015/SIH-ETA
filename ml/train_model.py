import pandas as pd
import numpy as np
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. LOAD REAL DATASET
# ============================================================

FILE = "features_ml_ready.xlsx"

print("=" * 60)
print("Loading dataset...")
print("=" * 60)

df = pd.read_excel(FILE)

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 2. BASIC CLEANING
# ============================================================

df["date"] = pd.to_datetime(df["date"])

# Sort chronologically.
# This helps us make a more realistic future-data test.
df = df.sort_values("date").reset_index(drop=True)

print("\nMissing values:")
print(df.isnull().sum()[df.isnull().sum() > 0])


# ============================================================
# 3. CREATE TIME FEATURES
# ============================================================

df["month"] = df["date"].dt.month
df["day_of_month"] = df["date"].dt.day

# We don't use the raw date directly.
df = df.drop(columns=["date"])


# ============================================================
# 4. TARGET
# ============================================================

TARGET = "target_final_delay_min"

print("\nTarget:", TARGET)

print("\nTarget statistics:")
print(df[TARGET].describe())


# ============================================================
# 5. SELECT FEATURES
# ============================================================

# These are useful operational features for predicting
# final destination delay.

numeric_features = [
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
    "day_of_month"
]

categorical_features = [
    "station_id",
    "station_name"
]


features = numeric_features + categorical_features

# Make sure all requested columns exist.
missing_features = [c for c in features if c not in df.columns]

if missing_features:
    raise ValueError(
        "These features are missing from the dataset: "
        + str(missing_features)
    )


# ============================================================
# 6. REMOVE ROWS WITH MISSING TARGET
# ============================================================

df = df.dropna(subset=[TARGET]).copy()

X = df[features]
y = df[TARGET]


print("\nTraining rows:", len(X))
print("Number of features:", len(features))


# ============================================================
# 7. CHRONOLOGICAL TRAIN/TEST SPLIT
# ============================================================

# First 80% = training
# Last 20%  = testing
#
# This is better than a random split for time-based railway
# prediction because we want to simulate predicting future data.

split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("\nTrain size:", X_train.shape)
print("Test size:", X_test.shape)


# ============================================================
# 8. PREPROCESSING
# ============================================================

numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)

categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=True
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_transformer,
            numeric_features
        ),
        (
            "categorical",
            categorical_transformer,
            categorical_features
        )
    ]
)


# ============================================================
# 9. RANDOM FOREST MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)


pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ============================================================
# 10. TRAIN
# ============================================================

print("\n" + "=" * 60)
print("Training Random Forest...")
print("=" * 60)

pipeline.fit(X_train, y_train)

print("Training complete.")


# ============================================================
# 11. EVALUATION
# ============================================================

predictions = pipeline.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

# Simple baseline:
# predict that future final delay will equal the current delay.
baseline_predictions = X_test["current_delay_min"]

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions
)


print("\n" + "=" * 60)
print("MODEL RESULTS")
print("=" * 60)

print(f"Baseline MAE : {baseline_mae:.2f} minutes")
print(f"Model MAE    : {mae:.2f} minutes")
print(f"Model RMSE   : {rmse:.2f} minutes")
print(f"Model R²     : {r2:.4f}")


# ============================================================
# 12. SAMPLE PREDICTIONS
# ============================================================

results = pd.DataFrame({
    "actual_delay": y_test.values,
    "predicted_delay": predictions,
    "error": y_test.values - predictions
})

print("\nSample predictions:")
print(results.head(10).to_string(index=False))


# ============================================================
# 13. SAVE MODEL
# ============================================================

MODEL_FILE = "eta_model.joblib"

joblib.dump(
    pipeline,
    MODEL_FILE
)

print("\n" + "=" * 60)
print(f"Model saved successfully: {MODEL_FILE}")
print("=" * 60)
