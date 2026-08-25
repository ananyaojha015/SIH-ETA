from dataclasses import dataclass


@dataclass
class PassengerReport:
    train_id: str
    type: str
    location: str
    timestamp: str
    description: str