import { useState } from "react";
import mockTrainData from "./data/mockTrainData";
import "./App.css";

function App() {
  const [additionalDelay, setAdditionalDelay] = useState("0");
  const [congestion, setCongestion] = useState("medium");
  const [simulation, setSimulation] = useState(null);

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

    const totalAdditionalDelay =
      delay + congestionImpact[congestion];

    const simulatedDelay = Math.max(
      0,
      mockTrainData.delay + totalAdditionalDelay
    );

    const [hours, minutes] = mockTrainData.eta
      .split(":")
      .map(Number);

    const baseMinutes = hours * 60 + minutes;

    const simulatedMinutes =
      baseMinutes + totalAdditionalDelay;

    const finalHours = Math.floor(simulatedMinutes / 60) % 24;
    const finalMinutes = simulatedMinutes % 60;

    const simulatedEta = `${String(finalHours).padStart(2, "0")}:${String(
      finalMinutes
    ).padStart(2, "0")}`;

    const simulatedRisk = Math.min(
      99,
      Math.max(
        5,
        mockTrainData.delayRisk +
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

  return (
    <div className="dashboard">

      {/* Header */}
      <header className="header">
        <div>
          <h1>🚆 ETA Intelligence</h1>
          <p>Dynamic Railway Monitoring System</p>
        </div>

        <div className="live-status">
          <span className="live-dot"></span>
          LIVE
        </div>
      </header>

      <main>

        {/* Railway Map */}
       {/* Railway Map */}
<section className="map-section">

  <div className="section-heading">
    <div>
      <div className="card-label">LIVE NETWORK</div>
      <h2>Railway Map</h2>
    </div>

    <div className="map-status">
      <span className="tracking-dot"></span>
      Live tracking
    </div>
  </div>

  <div className="railway-map">

    {/* Track */}
    <div className="track-base"></div>
    <div className="track-glow"></div>

    {/* Moving train */}
    <div className="train-position">
      <div className="train-marker">
        🚆
      </div>
      <span className="train-label">
        Train {mockTrainData.trainId}
      </span>
    </div>

    {/* Delhi */}
    <div className="station station-one">

      <div className="station-node completed">
        <span></span>
      </div>

      <div className="station-info">
        <strong>Delhi</strong>
        <span>Departed</span>
      </div>

    </div>

    {/* Kanpur */}
    <div className="station station-two">

      <div className="station-node current">
        <span></span>
      </div>

      <div className="station-info">
        <strong>Kanpur</strong>
        <span>Current location</span>
      </div>

    </div>

    {/* Lucknow */}
    <div className="station station-three">

      <div className="station-node upcoming">
        <span></span>
      </div>

      <div className="station-info">
        <strong>Lucknow</strong>
        <span>Upcoming</span>
      </div>

    </div>

  </div>

</section>
        {/* Train + ETA */}
        <section className="train-section">

          {/* Train Card */}
          <div className="train-card">

            <div className="card-label">
              LIVE TRAIN
            </div>

            <h2>
              Train {mockTrainData.trainId}
            </h2>

            <p className="route">
              {mockTrainData.route.from}
              {" → "}
              {mockTrainData.route.destination}
            </p>

            <div className="train-details">

              <div>
                <span>Current Station</span>

                <strong>
                  {mockTrainData.route.current}
                </strong>
              </div>

              <div>
                <span>Speed</span>

                <strong>
                  {mockTrainData.speed} km/h
                </strong>
              </div>

              <div>
                <span>Delay</span>

                <strong className="delay">
                  +{mockTrainData.delay} min
                </strong>
              </div>

            </div>

          </div>

          {/* ETA Card */}
          <div className="eta-card">

            <div className="card-label">
              PREDICTED ARRIVAL
            </div>

            <div className="eta-time">
              {mockTrainData.eta}
            </div>

            <p className="eta-range">
              Expected range:{" "}
              <strong>
                {mockTrainData.etaRange.min}
                {" – "}
                {mockTrainData.etaRange.max}
              </strong>
            </p>

            <div className="confidence">

              <span>
                Prediction Confidence
              </span>

              <strong>
                {mockTrainData.confidence}%
              </strong>

            </div>

            <div className="confidence-bar">
              <div
                className="confidence-fill"
                style={{
                  width: `${mockTrainData.confidence}%`,
                }}
              ></div>
            </div>

          </div>

        </section>

        {/* Delay Risk */}
        <section className="risk-section">

          <div>
            <div className="card-label">
              DELAY FORECAST
            </div>

            <h2>
              Delay Risk
            </h2>

            <div className="risk-value">
              {mockTrainData.delayRisk}%
            </div>

            <p className="risk-status">
              Medium Risk
            </p>
          </div>

          <div className="risk-info">

            <p>
              Current delay and congestion indicate a
              moderate probability of further delay.
            </p>

          </div>

        </section>

        {/* Why ETA Changed */}
        <section className="why-section">

          <div className="card-label">
            ETA EXPLANATION
          </div>

          <h2>
            🧠 Why did ETA change?
          </h2>

          <p className="explanation">
            The predicted arrival time increased because
            the train is currently experiencing operational
            delay and congestion near{" "}
            {mockTrainData.route.current}.
          </p>

          <div className="factor-list">

            {mockTrainData.etaFactors.map((factor) => (

              <div
                className="factor"
                key={factor.name}
              >

                <div className="factor-header">

                  <span>
                    {factor.name}
                  </span>

                  <strong>
                    {factor.percentage}%
                  </strong>

                </div>

                <div className="factor-bar">

                  <div
                    className="factor-fill"
                    style={{
                      width: `${factor.percentage}%`,
                    }}
                  ></div>

                </div>

              </div>

            ))}

          </div>

        </section>

        {/* Journey Timeline */}
        <section className="timeline-section">

          <div className="card-label">
            JOURNEY PROGRESS
          </div>

          <h2>
            Journey Timeline
          </h2>

          <div className="timeline">

            {mockTrainData.timeline.map((item) => (

              <div
                className={`timeline-item ${item.status}`}
                key={item.station}
              >

                <div className="timeline-dot">

                  {item.status === "completed"
                    ? "✓"
                    : item.status === "current"
                    ? "●"
                    : "○"}

                </div>

                <div className="timeline-content">

                  <strong>
                    {item.station}
                  </strong>

                  <span>
                    {item.information}
                  </span>

                </div>

              </div>

            ))}

          </div>

        </section>

        {/* Passenger Updates */}
        <section className="passenger-section">

          <div className="card-label">
            CROWD INTELLIGENCE
          </div>

          <h2>
            👥 Passenger Updates
          </h2>

          <div className="passenger-reports">

            {mockTrainData.passengerReports.map((report) => (

              <div
                className="passenger-report"
                key={report.title}
              >

                <div className="report-icon">
                  {report.icon}
                </div>

                <div className="report-content">

                  <strong>
                    {report.title}
                  </strong>

                  <p>
                    {report.description}
                  </p>

                  <span>
                    {report.reports} reports
                    {" · "}
                    {report.confidence} confidence
                    {" · "}
                    {report.time}
                  </span>

                </div>

              </div>

            ))}

          </div>

        </section>

        {/* What-if Simulation */}
        <section className="what-if-section">

          <div className="card-label">
            SCENARIO SIMULATION
          </div>

          <h2>
            🔮 What-if Simulation
          </h2>

          <p>
            Test how operational changes could affect
            the predicted arrival time.
          </p>

          <div className="simulation-controls">

            <div className="simulation-option">

              <label>
                Additional Delay
              </label>

              <select
                value={additionalDelay}
                onChange={(event) =>
                  setAdditionalDelay(event.target.value)
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
                  setCongestion(event.target.value)
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

          <button
            className="simulate-button"
            onClick={runSimulation}
          >
            Run Simulation
          </button>

          {/* Simulation Result */}
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
                Under this scenario, the predicted arrival
                changes to <strong>{simulation.eta}</strong>{" "}
                with an estimated delay of{" "}
                <strong>+{simulation.delay} minutes</strong>.
                The calculated delay risk is{" "}
                <strong>{simulation.risk}%</strong>.
              </p>

            </div>
          )}

        </section>

      </main>

      <footer className="footer">
        SIH ETA Intelligence · Railway Delay Prediction System
      </footer>

    </div>
  );
}

export default App;