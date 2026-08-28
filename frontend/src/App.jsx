
import { useEffect, useState } from "react";
import mockTrainData from "./data/mockTrainData";

import {
  getTrain,
  getETA,
  getTimeline,
  getReports,
  triggerTrainEvent,
} from "./api/api.js";

import "./App.css";

const REPORT_TYPES = [
  "train_stopped",
  "moving_slowly",
  "heavy_crowd",
  "platform_changed",
  "weather_issue",
  "announcement",
  "accident",
  "medical_emergency",
  "fire_smoke",
  "security_concern",
  "track_obstruction",
];

const formatBreakdownName = (key) => {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
};

function App() {
  const [trainData, setTrainData] = useState(mockTrainData);
  const [etaData, setEtaData] = useState(null);
  const [timelineData, setTimelineData] = useState(null);
  const [reportsData, setReportsData] = useState(null);

  const [backendConnected, setBackendConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  const [congestionLoading, setCongestionLoading] = useState(false);
  const [congestionMessage, setCongestionMessage] = useState("");

  const [additionalDelay, setAdditionalDelay] = useState("0");
  const [congestion, setCongestion] = useState("medium");
  const [simulation, setSimulation] = useState(null);

  const [reportType, setReportType] = useState("train_stopped");

  const TRAIN_ID = "12876";

  /* =========================
     LOAD BACKEND DATA
  ========================= */

  const loadBackendData = async () => {
    try {
      const [train, eta, timeline, reports] =
        await Promise.all([
          getTrain(TRAIN_ID),
          getETA(TRAIN_ID),
          getTimeline(TRAIN_ID),
          getReports(TRAIN_ID),
        ]);

      setTrainData(train);
      setEtaData(eta);
      setTimelineData(timeline);
      setReportsData(reports);

      setBackendConnected(true);
      setLoading(false);
    } catch (error) {
      console.error("Backend connection failed:", error);

      setBackendConnected(false);
      setLoading(false);
    }
  };

  /* =========================
     INITIAL LOAD + POLLING
  ========================= */

  useEffect(() => {
    loadBackendData();

    const interval = setInterval(() => {
      loadBackendData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  /* =========================
     REAL BACKEND CONGESTION
  ========================= */

  const triggerCongestion = async () => {
    console.log(
      "🚦 Triggering CONGESTION for train:",
      TRAIN_ID
    );

    setCongestionLoading(true);
    setCongestionMessage("");

    try {
      const eventResponse = await triggerTrainEvent(
        TRAIN_ID,
        "CONGESTION"
      );

      console.log(
        "✅ Congestion event response:",
        eventResponse
      );

      const updatedTrain = await getTrain(TRAIN_ID);
      const updatedETA = await getETA(TRAIN_ID);

      setTrainData(updatedTrain);
      setEtaData(updatedETA);

      setBackendConnected(true);

      setCongestionMessage(
        "✓ Congestion applied — ETA updated"
      );

      try {
        const updatedTimeline =
          await getTimeline(TRAIN_ID);

        const updatedReports =
          await getReports(TRAIN_ID);

        setTimelineData(updatedTimeline);
        setReportsData(updatedReports);
      } catch (refreshError) {
        console.warn(
          "Optional refresh failed:",
          refreshError
        );
      }
    } catch (error) {
      console.error(
        "❌ Congestion trigger failed:",
        error
      );

      setCongestionMessage(
        `✕ Failed: ${error.message}`
      );

      setBackendConnected(false);
    } finally {
      setCongestionLoading(false);
    }
  };

  /* =========================
     WHAT-IF SIMULATION
  ========================= */

  const runSimulation = () => {
    const delay = Number(additionalDelay);

    const congestionImpact = {
      low: -2,
      medium: 0,
      high: 10,
    };

    const congestionRisk = {
      low: -12,
      medium: 0,
      high: 18,
    };

    const baseDelay =
      etaData?.delay_risk !== undefined
        ? Math.round(etaData.delay_risk / 10)
        : mockTrainData.delay;

    const totalAdditionalDelay =
      delay + congestionImpact[congestion];

    const simulatedDelay = Math.max(
      0,
      baseDelay + totalAdditionalDelay
    );

    const baseEta =
      etaData?.eta || mockTrainData.eta;

    const [hours, minutes] = baseEta
      .split(":")
      .map(Number);

    const baseMinutes = hours * 60 + minutes;

    const simulatedMinutes =
      baseMinutes + totalAdditionalDelay;

    const finalHours =
      Math.floor(simulatedMinutes / 60) % 24;

    const finalMinutes =
      simulatedMinutes % 60;

    const simulatedEta =
      `${String(finalHours).padStart(
        2,
        "0"
      )}:${String(finalMinutes).padStart(
        2,
        "0")}`;

    const baseRisk =
      etaData?.delay_risk ??
      mockTrainData.delayRisk;

    const simulatedRisk = Math.min(
      99,
      Math.max(
        5,
        baseRisk +
          delay * 1.5 +
          congestionRisk[congestion]
      )
    );

    let riskStatus = "Low Risk";

    if (simulatedRisk >= 70) {
      riskStatus = "High Risk";
    } else if (simulatedRisk >= 40) {
      riskStatus = "Medium Risk";
    }

    setSimulation({
      eta: simulatedEta,
      delay: Math.round(simulatedDelay),
      risk: Math.round(simulatedRisk),
      riskStatus,
    });
  };

  /* =========================
     NORMALIZED DATA
  ========================= */

  const currentStation =
    trainData?.current_station ||
    trainData?.route?.current ||
    mockTrainData.route.current;

  const nextStation =
    trainData?.next_station ||
    "Station C";

  const currentDelay =
    trainData?.delay_min ??
    trainData?.delay ??
    mockTrainData.delay;

  const trainStatus =
    trainData?.status ||
    "running";

  const speed =
    trainData?.speed ??
    mockTrainData.speed;

  const currentEta =
    etaData?.eta ||
    mockTrainData.eta;

  const etaMin =
    etaData?.eta_min ||
    mockTrainData.etaRange.min;

  const etaMax =
    etaData?.eta_max ||
    mockTrainData.etaRange.max;

  const confidence =
    etaData?.confidence ??
    mockTrainData.confidence;

  const delayRisk =
    etaData?.delay_risk ??
    mockTrainData.delayRisk;

  const timeline =
    timelineData?.timeline ||
    mockTrainData.timeline;

  const reports =
    reportsData?.reports ||
    mockTrainData.passengerReports ||
    [];

  const verification =
    reportsData?.verification ||
    null;

  /* =========================
     DYNAMIC ETA BREAKDOWN
  ========================= */

  const breakdown =
    etaData?.breakdown || {};

  const breakdownFactors = Object.entries(
    breakdown
  ).filter(
    ([, percentage]) =>
      Number(percentage) > 0
  );

  return (
    <div className="dashboard">

      {/* HEADER */}

      <header className="header">

        <div>
          <h1>
            🚆 ETA Intelligence
          </h1>

          <p>
            Dynamic Railway Monitoring System
          </p>
        </div>

        <div className="live-status">

          <span className="live-dot"></span>

          {backendConnected
            ? "LIVE"
            : "BACKEND OFFLINE"}

        </div>

      </header>

      <main>

        {/* BACKEND STATUS */}

        {!backendConnected && (
          <div
            style={{
              padding: "10px 16px",
              marginBottom: "15px",
              borderRadius: "8px",
              background:
                "rgba(255, 165, 0, 0.12)",
              border:
                "1px solid rgba(255, 165, 0, 0.3)",
            }}
          >
            ⚠️ Backend unavailable —
            showing available data.
          </div>
        )}

        {/* RAILWAY MAP */}

        <section className="map-section">

          <div className="section-heading">

            <div>

              <div className="card-label">
                LIVE NETWORK
              </div>

              <h2>
                Railway Map
              </h2>

            </div>

            <div className="map-status">
              ● Live tracking
            </div>

          </div>

          <div className="railway-map">

            <div className="route-line"></div>

            <div className="station station-one">

              <div className="station-dot"></div>

              <span>
                Delhi
              </span>

            </div>

            <div className="station station-two">

              <div className="station-dot current"></div>

              <div className="train-marker">
                🚆
              </div>

              <span>
                {currentStation}
              </span>

            </div>

            <div className="station station-three">

              <div className="station-dot"></div>

              <span>
                Lucknow
              </span>

            </div>

          </div>

        </section>

        {/* TRAIN + ETA */}

        <section className="train-section">

          <div className="train-card">

            <div className="card-label">
              LIVE TRAIN
            </div>

            <h2>
              Train{" "}
              {trainData?.train_id ||
                mockTrainData.trainId}
            </h2>

            <p className="route">
              {mockTrainData.route.from}
              {" → "}
              {mockTrainData.route.destination}
            </p>

            <div className="train-details">

              <div>
                <span>
                  Current Station
                </span>

                <strong>
                  {currentStation}
                </strong>
              </div>

              <div>
                <span>
                  Speed
                </span>

                <strong>
                  {speed} km/h
                </strong>
              </div>

              <div>
                <span>
                  Delay
                </span>

                <strong className="delay">
                  +{currentDelay} min
                </strong>
              </div>

            </div>

            <div
              style={{
                marginTop: "12px",
                fontSize: "13px",
                opacity: 0.7,
              }}
            >
              Status: {trainStatus}
              {" · "}
              Next: {nextStation}
            </div>

          </div>

          {/* ETA CARD */}

          <div className="eta-card">

            <div className="card-label">
              PREDICTED ARRIVAL
            </div>

            <div className="eta-time">
              {currentEta}
            </div>

            <p className="eta-range">
              Expected range:{" "}
              <strong>
                {etaMin} – {etaMax}
              </strong>
            </p>

            <div className="confidence">

              <span>
                Prediction Confidence
              </span>

              <strong>
                {confidence}%
              </strong>

            </div>

            <div className="confidence-bar">

              <div
                className="confidence-fill"
                style={{
                  width:
                    `${confidence}%`,
                }}
              ></div>

            </div>

          </div>

        </section>

        {/* DELAY RISK */}

        <section className="risk-section">

          <div>

            <div className="card-label">
              DELAY FORECAST
            </div>

            <h2>
              Delay Risk
            </h2>

            <div className="risk-value">
              {delayRisk}%
            </div>

            <p className="risk-status">
              {delayRisk >= 70
                ? "High Risk"
                : delayRisk >= 40
                ? "Medium Risk"
                : "Low Risk"}
            </p>

          </div>

          <div className="risk-info">

            <p>
              Current delay and
              congestion indicate a
              moderate probability of
              further delay.
            </p>

          </div>

        </section>

        {/* WHY ETA CHANGED */}

        <section className="why-section">

          <div className="card-label">
            ETA EXPLANATION
          </div>

          <h2>
            🧠 Why did ETA change?
          </h2>

          <p className="explanation">
            The predicted arrival time is
            influenced by the current
            operational conditions and
            live railway data.
          </p>

          <div className="factor-list">

            {breakdownFactors.length > 0 ? (

              breakdownFactors.map(
                ([key, percentage]) => (

                  <div
                    className="factor"
                    key={key}
                  >

                    <div className="factor-header">

                      <span>
                        {formatBreakdownName(
                          key
                        )}
                      </span>

                      <strong>
                        {percentage}%
                      </strong>

                    </div>

                    <div className="factor-bar">

                      <div
                        className="factor-fill"
                        style={{
                          width:
                            `${percentage}%`,
                        }}
                      ></div>

                    </div>

                  </div>

                )
              )

            ) : (

              <p
                style={{
                  opacity: 0.7,
                  fontSize: "14px",
                }}
              >
                No ETA breakdown available yet.
              </p>

            )}

          </div>

        </section>

        {/* TIMELINE */}

        <section className="timeline-section">

          <div className="card-label">
            JOURNEY PROGRESS
          </div>

          <h2>
            Journey Timeline
          </h2>

          <div className="timeline">

            {timeline.map(
              (item, index) => (

                <div
                  className={`timeline-item ${
                    item.status ||
                    "future"
                  }`}
                  key={
                    item.station ||
                    index
                  }
                >

                  <div className="timeline-dot">

                    {item.status ===
                      "past" ||
                    item.status ===
                      "completed"
                      ? "✓"
                      : item.status ===
                        "current"
                      ? "●"
                      : "○"}

                  </div>

                  <div className="timeline-content">

                    <strong>
                      {item.station}
                    </strong>

                    <span>
                      {item.information ||
                        item.actual ||
                        item.eta ||
                        "Scheduled"}
                    </span>

                  </div>

                </div>

              )
            )}

          </div>

        </section>

        {/* PASSENGER UPDATES */}

        <section className="passenger-section">

          <div className="card-label">
            CROWD INTELLIGENCE
          </div>

          <h2>
            👥 Passenger Updates
          </h2>

          {/* ONE COMBINED VERIFICATION SUMMARY */}

          {verification && (
            <div className="crowd-verification">

              <div className="verification-header">

                <div>

                  <span className="verification-label">
                    CROWD VERIFICATION
                  </span>

                  <strong>
                    {verification.report_count ??
                      reports.length}{" "}
                    matching reports
                  </strong>

                </div>

                <span
                  className={`verification-badge ${
                    verification.confidence
                      ?.toLowerCase()
                  }`}
                >
                  {verification.confidence ||
                    "Low"}{" "}
                  Confidence
                </span>

              </div>

              <p>
                {verification.summary ||
                  "Crowd verification is being calculated."}
              </p>

            </div>
          )}

          {/* REPORT TYPE */}

          <div
            style={{
              marginTop: "18px",
              marginBottom: "18px",
            }}
          >

            <label
              style={{
                display: "block",
                marginBottom: "8px",
                fontWeight: 600,
              }}
            >
              Report Type
            </label>

            <select
              value={reportType}
              onChange={(event) =>
                setReportType(
                  event.target.value
                )
              }
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: "8px",
                border: "1px solid rgba(128,128,128,0.3)",
                background: "inherit",
              }}
            >

              {REPORT_TYPES.map(
                (type) => (

                  <option
                    value={type}
                    key={type}
                  >
                    {formatBreakdownName(type)}
                  </option>

                )
              )}

            </select>

          </div>

          {/* INDIVIDUAL REPORTS */}

          <div className="passenger-reports">

            {reports.length === 0 ? (

              <p>
                No passenger reports yet.
              </p>

            ) : (

              reports.map(
                (report, index) => (

                  <div
                    className="passenger-report"
                    key={
                      report.id ||
                      report.description ||
                      index
                    }
                  >

                    <div className="report-icon">
                      {report.icon ||
                        "🚆"}
                    </div>

                    <div className="report-content">

                      <strong>
                        {report.title ||
                          formatBreakdownName(
                            report.type ||
                              "passenger_report"
                          )}
                      </strong>

                      <p>
                        {report.description ||
                          `Report near ${
                            report.location ||
                            "current location"
                          }`}
                      </p>

                      <span>
                        {report.location ||
                          "Current location"}
                        {" · "}
                        {report.time ||
                          "Recently"}
                      </span>

                    </div>

                  </div>

                )
              )

            )}

          </div>

        </section>

        {/* WHAT IF */}

        <section className="what-if-section">

          <div className="card-label">
            SCENARIO SIMULATION
          </div>

          <h2>
            🔮 What-if Simulation
          </h2>

          <p>
            Test how operational changes
            could affect the predicted
            arrival time.
          </p>

          <div className="simulation-controls">

            <div className="simulation-option">

              <label>
                Additional Delay
              </label>

              <select
                value={additionalDelay}
                onChange={(event) =>
                  setAdditionalDelay(
                    event.target.value
                  )
                }
              >

                <option value="0">
                  No additional delay
                </option>

                <option value="5">
                  +5 minutes
                </option>

                <option value="10">
                  +10 minutes
                </option>

                <option value="20">
                  +20 minutes
                </option>

              </select>

            </div>

            <div className="simulation-option">

              <label>
                Congestion
              </label>

              <select
                value={congestion}
                onChange={(event) =>
                  setCongestion(
                    event.target.value
                  )
                }
              >

                <option value="low">
                  Low
                </option>

                <option value="medium">
                  Medium
                </option>

                <option value="high">
                  High
                </option>

              </select>

            </div>

          </div>

          {/* REAL BACKEND EVENT */}

          <button
            className="simulate-button"
            onClick={triggerCongestion}
            disabled={congestionLoading}
          >
            {congestionLoading
              ? "⏳ Updating ETA..."
              : "🚦 Trigger Congestion"}
          </button>

          {congestionMessage && (
            <div
              style={{
                marginTop: "12px",
                fontSize: "13px",
                fontWeight: 600,
              }}
            >
              {congestionMessage}
            </div>
          )}

          {/* LOCAL WHAT-IF */}

          <button
            className="simulate-button"
            onClick={runSimulation}
            style={{
              marginTop: "12px",
              opacity: 0.85,
            }}
          >
            🔮 Run What-if Simulation
          </button>

          {/* SIMULATION RESULT */}

          {simulation && (

            <div className="simulation-result">

              <div className="simulation-result-header">

                <div>

                  <div className="card-label">
                    SIMULATION RESULT
                  </div>

                  <h3>
                    Scenario Prediction
                  </h3>

                </div>

                <span className="simulation-badge">
                  SIMULATED
                </span>

              </div>

              <div className="simulation-result-grid">

                <div className="simulation-result-card">

                  <span>
                    Simulated ETA
                  </span>

                  <strong className="simulated-eta">
                    {simulation.eta}
                  </strong>

                </div>

                <div className="simulation-result-card">

                  <span>
                    Expected Delay
                  </span>

                  <strong className="simulated-delay">
                    +{simulation.delay} min
                  </strong>

                </div>

                <div className="simulation-result-card">

                  <span>
                    Delay Risk
                  </span>

                  <strong className="simulated-risk">
                    {simulation.risk}%
                  </strong>

                  <small>
                    {simulation.riskStatus}
                  </small>

                </div>

              </div>

              <p className="simulation-explanation">

                Under this scenario,
                the predicted arrival
                changes to{" "}
                <strong>
                  {simulation.eta}
                </strong>{" "}
                with an estimated delay
                of{" "}
                <strong>
                  +{simulation.delay} minutes
                </strong>
                . The calculated delay
                risk is{" "}
                <strong>
                  {simulation.risk}%
                </strong>
                .

              </p>

            </div>

          )}

        </section>

      </main>

      <footer className="footer">
        SIH ETA Intelligence · Railway
        Delay Prediction System
      </footer>

    </div>
  );
}

export default App;

