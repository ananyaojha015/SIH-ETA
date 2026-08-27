import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SIM_PATH = os.path.join(PROJECT_ROOT, "simulation")
sys.path.append(SIM_PATH)

from trains import Train
from railway import STATIONS, get_next_station, get_distance
from simulation import get_train_state as sim_get_train_state
from events import event_congestion, event_delay, event_stoppage, event_station_dwell, event_normal

# In-memory train registry (Day 2 scope: single demo train, persists across requests)
_trains = {}
_last_event = {}  # train_id -> last event name, used to estimate congestion


def _get_or_create_train(train_id: str) -> Train:
    if train_id not in _trains:
        t = Train(train_id=train_id, current_station="Station A", speed=62)
        t.next_station = get_next_station(t.current_station)
        _trains[train_id] = t
        _last_event[train_id] = "NORMAL"
    return _trains[train_id]


def _calc_distance_remaining(train: Train) -> float:
    """Sum of distance from current position to the end of the route."""
    total = 0
    station = train.current_station
    # if currently between stations, count the rest of this section
    if train.next_station:
        d = get_distance(station, train.next_station)
        total += d if d else 0
        station = train.next_station
    # add all remaining sections after that
    nxt = get_next_station(station)
    while nxt:
        d = get_distance(station, nxt)
        total += d if d else 0
        station = nxt
        nxt = get_next_station(station)
    return total


def _estimate_congestion(train_id: str) -> float:
    """Day 2 placeholder: derive a rough congestion value from the last event."""
    event = _last_event.get(train_id, "NORMAL")
    mapping = {
        "NORMAL": 0.2,
        "STATION_DWELL": 0.3,
        "DELAY": 0.4,
        "CONGESTION": 0.75,
        "STOPPAGE": 0.9,
    }
    return mapping.get(event, 0.3)


def get_current_state(train_id: str) -> dict:
    train = _get_or_create_train(train_id)
    return sim_get_train_state(train)


def get_ml_inputs(train_id: str) -> dict:
    """Builds the exact inputs predict_eta() needs, from live simulation state."""
    train = _get_or_create_train(train_id)
    return {
        "speed": train.speed,
        "delay": train.delay,
        "distance_remaining": _calc_distance_remaining(train),
        "dwell_time": train.dwell_time,
        "congestion": _estimate_congestion(train_id),
    }


def trigger_event(train_id: str, event_type: str) -> dict:
    """Applies an event to the train (used for what-if / demo triggers)."""
    train = _get_or_create_train(train_id)
    if event_type == "CONGESTION":
        event_congestion(train, speed_drop=15, extra_delay=5)
    elif event_type == "DELAY":
        event_delay(train, extra_minutes=6)
    elif event_type == "STOPPAGE":
        event_stoppage(train, stop_minutes=8)
    elif event_type == "STATION_DWELL":
        event_station_dwell(train, extra_minutes=4)
    else:
        event_normal(train)
    _last_event[train_id] = event_type
    return sim_get_train_state(train)