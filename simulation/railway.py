# railway.py
# Defines the railway route: a simple line of stations

STATIONS = ["Station A", "Station B", "Station C", "Station D"]

SECTION_DISTANCES = {
    ("Station A", "Station B"): 20,
    ("Station B", "Station C"): 25,
    ("Station C", "Station D"): 18,
}

def get_next_station(current_station):
    """Returns the next station on the route, or None if at the end."""
    if current_station not in STATIONS:
        return None
    idx = STATIONS.index(current_station)
    if idx + 1 < len(STATIONS):
        return STATIONS[idx + 1]
    return None

def get_distance(station_a, station_b):
    """Returns distance between two consecutive stations."""
    return SECTION_DISTANCES.get((station_a, station_b), None)