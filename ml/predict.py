import os
from datetime import datetime, timedelta

import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "eta_model.joblib"
)

model = joblib.load(MODEL_PATH)


def predict_eta(
    speed,
    delay,
    distance_remaining,
    dwell_time,
    congestion
):
    """
    Day 2 ML interface.

    Inputs:
        speed              : current train speed in km/h
        delay              : current delay in minutes
        distance_remaining : remaining distance in km
        dwell_time         : expected dwell time in minutes
        congestion         : congestion level (0-1)

    Returns:
        eta
        eta_min
        eta_max
        confidence
        delay_risk
    """

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    speed = max(float(speed), 1.0)
    delay = max(float(delay), 0.0)
    distance_remaining = max(float(distance_remaining), 0.0)
    dwell_time = max(float(dwell_time), 0.0)
    congestion = min(max(float(congestion), 0.0), 1.0)

    # ---------------------------------------------------------
    # Simple ETA calculation
    #
    # This is the Day 2 adapter calculation.
    # The trained Random Forest remains responsible for
    # final-delay prediction when its full feature set is
    # available.
    # ---------------------------------------------------------

    travel_minutes = (distance_remaining / speed) * 60

    congestion_factor = 1.0 + (0.5 * congestion)

    estimated_minutes = (
        travel_minutes * congestion_factor
        + dwell_time
        + delay
    )

    # ---------------------------------------------------------
    # ETA range
    # ---------------------------------------------------------

    margin = max(2.0, estimated_minutes * 0.15)

    eta_min_minutes = max(
        0.0,
        estimated_minutes - margin
    )

    eta_max_minutes = (
        estimated_minutes + margin
    )

    # ---------------------------------------------------------
    # Confidence
    # ---------------------------------------------------------

    confidence = 100 - (
        congestion * 35
        + min(delay, 30) * 0.5
    )

    confidence = max(
        40,
        min(95, confidence)
    )

    # ---------------------------------------------------------
    # Delay risk
    # ---------------------------------------------------------

    delay_risk = (
        congestion * 60
        + min(delay, 20) * 2
        + min(dwell_time, 10) * 1.5
    )

    delay_risk = max(
        0,
        min(100, delay_risk)
    )

    # ---------------------------------------------------------
    # Convert ETA minutes into clock times
    # ---------------------------------------------------------

    now = datetime.now()

    eta_time = now + timedelta(
        minutes=estimated_minutes
    )

    eta_min_time = now + timedelta(
        minutes=eta_min_minutes
    )

    eta_max_time = now + timedelta(
        minutes=eta_max_minutes
    )

    return {
        "eta": eta_time.strftime("%H:%M"),
        "eta_min": eta_min_time.strftime("%H:%M"),
        "eta_max": eta_max_time.strftime("%H:%M"),
        "confidence": round(confidence),
        "delay_risk": round(delay_risk),
    }