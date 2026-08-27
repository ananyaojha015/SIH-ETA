const API_BASE_URL = "http://localhost:8000";

export async function getTrain(trainId) {
  const response = await fetch(
    `${API_BASE_URL}/train/${trainId}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch train data");
  }

  return response.json();
}

export async function getETA(trainId) {
  const response = await fetch(
    `${API_BASE_URL}/train/${trainId}/eta`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch ETA data");
  }

  return response.json();
}

export async function getTimeline(trainId) {
  const response = await fetch(
    `${API_BASE_URL}/train/${trainId}/timeline`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch timeline");
  }

  return response.json();
}

export async function getReports(trainId) {
  const response = await fetch(
    `${API_BASE_URL}/reports/${trainId}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch passenger reports");
  }

  return response.json();
}