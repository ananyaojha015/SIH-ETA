const mockTrainData = {
  trainId: "12876",

  route: {
    from: "Delhi",
    current: "Kanpur",
    destination: "Lucknow",
  },

  speed: 62,
  delay: 9,

  eta: "18:47",

  etaRange: {
    min: "18:44",
    max: "18:51",
  },

  confidence: 91,
  delayRisk: 68,

  timeline: [
    {
      station: "Delhi",
      status: "completed",
      information: "Departure — 17:52",
    },
    {
      station: "Kanpur",
      status: "current",
      information: "Current location — +9 min delay",
    },
    {
      station: "Lucknow",
      status: "upcoming",
      information: "Estimated arrival — 18:47",
    },
  ],

  etaFactors: [
    {
      name: "Congestion",
      percentage: 38,
    },
    {
      name: "Dwell Time",
      percentage: 24,
    },
    {
      name: "Current Delay",
      percentage: 18,
    },
    {
      name: "Speed Reduction",
      percentage: 12,
    },
  ],

  passengerReports: [
    {
      icon: "⚠️",
      title: "Temporary stoppage reported",
      description:
        "Multiple passengers report that the train has stopped near Kanpur.",
      reports: 12,
      confidence: "High",
      time: "4 min ago",
    },
    {
      icon: "🐌",
      title: "Slow movement reported",
      description:
        "Passengers report reduced speed after leaving the previous station.",
      reports: 7,
      confidence: "Medium",
      time: "8 min ago",
    },
  ],
};

export default mockTrainData;