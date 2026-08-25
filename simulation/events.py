# events.py
# Handles delay/dwell events

def apply_dwell_increase(train, extra_minutes):
    """Simulates a dwell time increase event at a station."""
    train.dwell_time += extra_minutes
    train.delay += extra_minutes
    train.status = "delayed"
    print(f"[EVENT] {train.train_id}: dwell increased by {extra_minutes} min "
          f"at {train.current_station}. Total delay: {train.delay} min")
    return train