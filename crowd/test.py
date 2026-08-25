from models import PassengerReport
from verification import verify_reports
from summary import generate_summary

reports = [
    PassengerReport(
        train_id="12876",
        type="train_stopped",
        location="Station B",
        timestamp="2026-08-25T10:30:00",
        description="Train stopped"
    ),

    PassengerReport(
        train_id="12876",
        type="train_stopped",
        location="Station B",
        timestamp="2026-08-25T10:31:00",
        description="Still stopped"
    ),

    PassengerReport(
        train_id="12876",
        type="train_stopped",
        location="Station B",
        timestamp="2026-08-25T10:32:00",
        description="Train has not moved"
    ),

    PassengerReport(
        train_id="12876",
        type="train_stopped",
        location="Station B",
        timestamp="2026-08-25T10:33:00",
        description="Unexpected halt"
    ),

    PassengerReport(
        train_id="12876",
        type="train_stopped",
        location="Station B",
        timestamp="2026-08-25T10:34:00",
        description="Train still stationary"
    )
]


result = verify_reports(reports)

print("Crowd Intelligence Result")
print("--------------------------")
print("Train:", result["train_id"])
print("Event:", result["type"])
print("Location:", result["location"])
print("Consistent Reports:", result["report_count"])
print("Confidence:", result["confidence"])