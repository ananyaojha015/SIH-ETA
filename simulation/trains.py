# trains.py
# Defines the Train class

class Train:
    def __init__(self, train_id, current_station, speed=60):
        self.train_id = train_id
        self.current_station = current_station
        self.next_station = None
        self.speed = speed          # km/h
        self.delay = 0              # minutes
        self.status = "at_station"  # at_station | moving | delayed
        self.position_km = 0        # progress in current section
        self.dwell_time = 2         # minutes default

    def to_dict(self):
        return {
            "train_id": self.train_id,
            "current_station": self.current_station,
            "next_station": self.next_station,
            "speed": self.speed,
            "delay": self.delay,
            "status": self.status,
            "position_km": self.position_km,
        }