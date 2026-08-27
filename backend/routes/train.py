from fastapi import APIRouter
from models import TrainStatus, ETAResponse, TimelineResponse
from services.ml_service import get_eta_prediction

router = APIRouter(prefix="/train", tags=["train"])


@router.get("/{train_id}", response_model=TrainStatus)
def get_train(train_id: str):
    return {
        "train_id": train_id,
        "current_station": "Station B",
        "next_station": "Station C",
        "delay_min": 9,
        "status": "running"
    }


@router.get("/{train_id}/eta", response_model=ETAResponse)
def get_eta(train_id: str):
    # TODO: replace these hardcoded values with real simulation
    # data from Ashwika's get_train_state() once it's wired in
    prediction = get_eta_prediction(
        speed=65,
        delay=9,
        distance_remaining=40,
        dwell_time=3,
        congestion=0.5,
    )

    return {
        "train_id": train_id,
        "eta": prediction["eta"],
        "eta_min": prediction["eta_min"],
        "eta_max": prediction["eta_max"],
        "confidence": prediction["confidence"],
        "delay_risk": prediction["delay_risk"],
    }


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