import sys
import os

# Add project root to path so we can import from /ml
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ML_PATH = os.path.join(PROJECT_ROOT, "ml")
sys.path.append(ML_PATH)

from predict import predict_eta


def get_eta_prediction(speed, delay, distance_remaining, dwell_time, congestion):
    """
    Wraps Anubha's predict_eta() so the rest of the backend
    doesn't need to know about the ml/ folder structure.
    """
    return predict_eta(
        speed=speed,
        delay=delay,
        distance_remaining=distance_remaining,
        dwell_time=dwell_time,
        congestion=congestion,
    )