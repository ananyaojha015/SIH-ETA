from fastapi import APIRouter
from models import TrainStatus, ETAResponse, TimelineResponse

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
    return {
        "train_id": train_id,
        "eta": "18:47",
        "eta_min": "18:44",
        "eta_max": "18:51",
        "confidence": 91,
        "delay_risk": 68
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