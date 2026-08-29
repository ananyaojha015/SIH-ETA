from fastapi import APIRouter
from models import TrainStatus, ETAResponse, TimelineResponse
from services.ml_service import get_eta_prediction
from services.simulation_service import get_current_state, get_ml_inputs, trigger_event
from services.reports_store import get_reports_for_train
from services.crowd_service import evaluate_reports
from services.explain_service import get_eta_breakdown

router = APIRouter(prefix="/train", tags=["train"])


@router.get("/{train_id}", response_model=TrainStatus)
def get_train(train_id: str):
    state = get_current_state(train_id)
    return {
        "train_id": state["train_id"],
        "current_station": state["position"],
        "next_station": state["next_station"] or "N/A",
        "delay_min": state["delay"],
        "status": state["status"],
    }


@router.get("/{train_id}/eta", response_model=ETAResponse)
def get_eta(train_id: str):
    ml_inputs = get_ml_inputs(train_id)
    prediction = get_eta_prediction(**ml_inputs)

    train_reports = get_reports_for_train(train_id)
    crowd_confidence = None
    crowd_report_count = 0
    if train_reports:
        verification = evaluate_reports(train_id, train_reports)
        crowd_confidence = verification.get("confidence")
        crowd_report_count = verification.get("report_count", 0)

    breakdown = get_eta_breakdown(
        speed=ml_inputs["speed"],
        delay=ml_inputs["delay"],
        dwell_time=ml_inputs["dwell_time"],
        congestion=ml_inputs["congestion"],
        crowd_confidence=crowd_confidence,
        crowd_report_count=crowd_report_count,
    )

    return {
        "train_id": train_id,
        "eta": prediction["eta"],
        "eta_min": prediction["eta_min"],
        "eta_max": prediction["eta_max"],
        "confidence": prediction["confidence"],
        "delay_risk": prediction["delay_risk"],
        "breakdown": breakdown,
    }


@router.post("/{train_id}/event/{event_type}")
def trigger_train_event(train_id: str, event_type: str):
    """Demo/what-if trigger: NORMAL, DELAY, CONGESTION, STOPPAGE, STATION_DWELL"""
    new_state = trigger_event(train_id, event_type.upper())
    return {"message": f"Event {event_type} applied", "new_state": new_state}


@router.get("/{train_id}/timeline", response_model=TimelineResponse)
def get_timeline(train_id: str):
    return {
        "train_id": train_id,
        "timeline": [
            {"station": "Station A", "actual": "17:52", "delay_min": 0, "status": "past"},
            {"station": "Station B", "actual": "18:21", "delay_min": 6, "status": "past"},
            {"station": "Station C", "eta": "18:39", "delay_min": 8, "status": "future"},
            {"station": "Destination", "eta": "19:17", "delay_min": 7, "status": "future"}
        ]
    }