# trains.py
# Defines the Train class

class Train:
    def __init__(self, train_id, current_station, speed=60):
        self.train_id = train_id
        self.current_station = current_station
        self.next_station = None
        self.speed = speed          # km/h
        self.delay = 0              # minutes
        self.status = "at_station"  # at_station | running | delayed | stopped
        self.position_km = 0        # progress in current section
        self.dwell_time = 2         # minutes default

    def get_position_label(self):
        """Returns a standardized position string for the backend."""
        def clean(name):
            return name.replace(" ", "_")

        if self.status == "at_station":
            return clean(self.current_station)
        if self.next_station:
            return f"between_{clean(self.current_station)}_{clean(self.next_station)}"
        return clean(self.current_station)

    def to_dict(self):
        """Standardized output format for backend integration."""
        return {
            "train_id": self.train_id,
            "position": self.get_position_label(),
            "speed": self.speed,
            "delay": self.delay,
            "next_station": self.next_station,
            "status": self.status,
        }