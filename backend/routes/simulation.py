from fastapi import APIRouter

router = APIRouter(prefix="/simulate", tags=["simulation"])

@router.post("/")
def run_simulation():
    return {
        "train_id": "12876",
        "position": "between_B_C",
        "speed": 62,
        "delay_min": 6,
        "next_station": "Station D"
    }