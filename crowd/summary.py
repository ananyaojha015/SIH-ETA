def generate_summary(result):

    event_names = {
        "train_stopped": "a train stoppage",
        "moving_slowly": "slow train movement",
        "heavy_crowd": "heavy crowding",
        "platform_changed": "a platform change",
        "weather_issue": "a weather-related issue",
        "announcement": "an announcement",
        "accident": "an accident",
        "medical_emergency": "a medical emergency",
        "fire_smoke": "a fire or smoke incident",
        "security_concern": "a security concern",
        "track_obstruction": "a track obstruction"

    }

    event = event_names.get(
        result["type"],
        "an unusual event"
    )

    location = result["location"]
    count = result["report_count"]
    confidence = result["confidence"]

    if confidence == "High":
        status = "The event has high crowd confirmation."

    elif confidence == "Medium":
        status = "The event has moderate crowd confirmation."

    else:
        status = "The event has not yet been officially confirmed."

    return (
        f"{count} passengers report {event} near "
        f"{location}. {status}"
    )