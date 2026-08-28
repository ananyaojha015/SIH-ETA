BASELINE_SPEED = 62

CROWD_CONFIDENCE_WEIGHT = {
    "Low": 5,
    "Medium": 15,
    "High": 25,
}


def get_eta_breakdown(speed, delay, dwell_time, congestion, crowd_confidence=None, crowd_report_count=0):
    """
    Day 2/3 explainability heuristic: turns the same inputs fed into
    predict_eta() into a percentage breakdown of what's driving the ETA.
    Not a real feature-importance score from the model — a transparent,
    interpretable approximation for the "Why?" panel.
    """
    congestion_score = congestion * 100
    dwell_score = dwell_time * 5
    delay_score = delay * 3
    speed_score = max(0, (BASELINE_SPEED - speed)) * 1.5

    crowd_score = 0
    if crowd_report_count > 0:
        crowd_score = CROWD_CONFIDENCE_WEIGHT.get(crowd_confidence, 0)

    raw = {
        "congestion": congestion_score,
        "dwell_time": dwell_score,
        "current_delay": delay_score,
        "speed_reduction": speed_score,
        "crowd_reports": crowd_score,
    }

    total = sum(raw.values())
    if total == 0:
        return {}

    breakdown = {k: round((v / total) * 100) for k, v in raw.items()}

    # rounding can drift the sum off 100 — correct on the largest factor
    diff = 100 - sum(breakdown.values())
    if diff != 0:
        top_key = max(breakdown, key=breakdown.get)
        breakdown[top_key] += diff

    # drop factors with 0% contribution for a cleaner display
    return {k: v for k, v in breakdown.items() if v > 0}