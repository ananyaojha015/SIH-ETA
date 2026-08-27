const API_BASE_URL = "http://127.0.0.1:8000";

async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `${response.status} ${response.statusText}: ${text}`
    );
  }

  return response.json();
}

export async function getTrain(trainId) {
  return request(
    `${API_BASE_URL}/train/${trainId}`
  );
}

export async function getETA(trainId) {
  return request(
    `${API_BASE_URL}/train/${trainId}/eta`
  );
}

export async function getTimeline(trainId) {
  return request(
    `${API_BASE_URL}/train/${trainId}/timeline`
  );
}

export async function getReports(trainId) {
  return request(
    `${API_BASE_URL}/reports/${trainId}`
  );
}

export async function triggerTrainEvent(
  trainId,
  eventType
) {
  return request(
    `${API_BASE_URL}/train/${trainId}/event/${eventType}`,
    {
      method: "POST",
    }
  );
}