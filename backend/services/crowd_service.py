import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from crowd.service import process_reports
from crowd.models import PassengerReport


def evaluate_reports(train_id: str, raw_reports: list[dict]) -> dict:
    """
    Takes the raw dict reports stored by the backend and runs them
    through Abhishek's verification + summary pipeline.
    """
    passenger_reports = [
        PassengerReport(
            train_id=r.get("train_id", ""),
            type=r.get("type", ""),
            location=r.get("location", ""),
            timestamp=r.get("timestamp", ""),
            description=r.get("description", ""),
        )
        for r in raw_reports
        if r.get("train_id") == train_id
    ]
    return process_reports(passenger_reports)