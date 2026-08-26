# events.py
# Handles all simulation events: NORMAL, DELAY, CONGESTION, STOPPAGE, STATION_DWELL

def event_normal(train):
    """Train running with no issues."""
    train.status = "running"
    print(f"[EVENT] {train.train_id}: NORMAL — running on schedule")
    return train


def event_delay(train, extra_minutes):
    """Generic delay added to the train."""
    train.delay += extra_minutes
    train.status = "delayed"
    print(f"[EVENT] {train.train_id}: DELAY — +{extra_minutes} min. Total delay: {train.delay} min")
    return train


def event_congestion(train, speed_drop=15, extra_delay=5):
    """Congestion ahead: speed decreases, delay increases."""
    train.speed = max(10, train.speed - speed_drop)
    train.delay += extra_delay
    train.status = "delayed"
    print(f"[EVENT] {train.train_id}: CONGESTION — speed now {train.speed} km/h, "
          f"delay +{extra_delay} min. Total delay: {train.delay} min")
    return train


def event_stoppage(train, stop_minutes=10):
    """Unexpected full stop (e.g. signal failure)."""
    train.speed = 0
    train.delay += stop_minutes
    train.status = "stopped"
    print(f"[EVENT] {train.train_id}: STOPPAGE — train halted for {stop_minutes} min. "
          f"Total delay: {train.delay} min")
    return train


def event_station_dwell(train, extra_minutes):
    """Extra dwell time at a station."""
    train.dwell_time += extra_minutes
    train.delay += extra_minutes
    train.status = "delayed"
    print(f"[EVENT] {train.train_id}: STATION_DWELL — dwell increased by {extra_minutes} min "
          f"at {train.current_station}. Total delay: {train.delay} min")
    return train


# Backward-compatible alias (in case simulation.py still imports the old name)
def apply_dwell_increase(train, extra_minutes):
    return event_station_dwell(train, extra_minutes)