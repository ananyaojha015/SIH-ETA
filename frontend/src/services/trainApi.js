import mockTrainData from "../data/mockTrainData";

export async function getTrain(trainId) {
  return {
    train_id: trainId,
    current_station: mockTrainData.route.current,
    next_station: mockTrainData.route.destination,
    delay_min: mockTrainData.delay,
    status: "running",
    speed: mockTrainData.speed,
  };
}

export async function getTrainETA(trainId) {
  return {
    train_id: trainId,
    eta: mockTrainData.eta,
    eta_min: mockTrainData.etaRange.min,
    eta_max: mockTrainData.etaRange.max,
    confidence: mockTrainData.confidence,
    delay_risk: mockTrainData.delayRisk,
  };
}

export async function getTimeline(trainId) {
  return {
    train_id: trainId,
    timeline: mockTrainData.timeline.map((item) => ({
      station: item.station,
      information: item.information,
      status:
        item.status === "completed"
          ? "past"
          : item.status === "current"
          ? "current"
          : "future",
    })),
  };
}

export async function getReports(trainId) {
  return {
    train_id: trainId,
    reports: mockTrainData.passengerReports,
  };
}