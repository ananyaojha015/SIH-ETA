from pydantic import BaseModel
from typing import Optional, List


class ETAResponse(BaseModel):
    train_id: str
    eta: str
    eta_min: str
    eta_max: str
    confidence: int
    delay_risk: int


class TrainStatus(BaseModel):
    train_id: str
    current_station: str
    next_station: str
    delay_min: int
    status: str


class TimelineStop(BaseModel):
    station: str
    delay_min: int
    status: str
    actual: Optional[str] = None
    eta: Optional[str] = None


class TimelineResponse(BaseModel):
    train_id: str
    timeline: List[TimelineStop]


class ReportCreate(BaseModel):
    train_id: str
    type: str
    location: str
    description: Optional[str] = None


class ReportResponse(BaseModel):
    message: str
    total_reports: int