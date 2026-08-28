from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class ReportType(str, Enum):
    train_stopped = "train_stopped"
    moving_slowly = "moving_slowly"
    heavy_crowd = "heavy_crowd"
    platform_changed = "platform_changed"
    weather_issue = "weather_issue"
    announcement = "announcement"
    accident = "accident"
    medical_emergency = "medical_emergency"
    fire_smoke = "fire_smoke"
    security_concern = "security_concern"
    track_obstruction = "track_obstruction"


class ETAResponse(BaseModel):
    train_id: str
    eta: str
    eta_min: str
    eta_max: str
    confidence: int
    delay_risk: int
    breakdown: Dict[str, int]


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
    type: ReportType
    location: str
    description: Optional[str] = None


class ReportResponse(BaseModel):
    message: str
    total_reports: int