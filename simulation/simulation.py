# simulation.py
from railway import STATIONS, get_next_station, get_distance
from trains import Train
from events import (
    event_normal,
    event_delay,
    event_congestion,
    event_stoppage,
    event_station_dwell,
)

def get_train_state(train):
    """Returns current train state as a dict — this is what backend will call."""
    return train.to_dict()

def move_train(train):
    """Moves the train one tick forward through the route."""
    train.next_station = get_next_station(train.current_station)

    if train.next_station is None:
        train.status = "arrived"
        print(f"{train.train_id} has arrived at final destination: {train.current_station}")
        return train

    distance = get_distance(train.current_station, train.next_station)
    train.status = "running"
    print(f"{train.train_id}: {train.current_station} -> {train.next_station} "
          f"(distance {distance} km, speed {train.speed} km/h, delay {train.delay} min)")

    train.current_station = train.next_station
    train.next_station = get_next_station(train.current_station)
    train.position_km = 0
    train.status = "at_station"
    print(f"{train.train_id} reached {train.current_station}")
    return train


def run_simulation():
    train = Train(train_id="12876", current_station="Station A", speed=62)

    print("=== SIMULATION START ===")
    event_normal(train)
    print(get_train_state(train))

    # Move A -> B
    move_train(train)
    print(get_train_state(train))

    # STATION_DWELL event at Station B
    event_station_dwell(train, extra_minutes=4)
    print(get_train_state(train))

    # Move B -> C
    move_train(train)
    print(get_train_state(train))

    # CONGESTION event near Station C
    event_congestion(train, speed_drop=15, extra_delay=5)
    print(get_train_state(train))

    # STOPPAGE event (e.g. signal failure)
    event_stoppage(train, stop_minutes=8)
    print(get_train_state(train))

    # Resume and move C -> D
    train.speed = 62
    move_train(train)
    print(get_train_state(train))

    print("=== SIMULATION END ===")


if __name__ == "__main__":
    run_simulation()