const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new ApiError(body || res.statusText, res.status);
  }
  return res.json();
}

export async function predict(data: {
  usia_bulan: number;
  jenis_kelamin: string;
  tinggi_cm: number;
  balita_id?: string;
}) {
  return request<{ status: string; data: import("./types").PredictResponse }>(
    "/predict",
    { method: "POST", body: JSON.stringify(data) }
  );
}

export async function getHistory(balitaId: string) {
  return request<{ status: string; data: import("./types").BalitaHistory }>(
    `/history/${balitaId}`
  );
}

export async function listHistory() {
  return request<{ status: string; data: import("./types").HistorySummary[] }>(
    "/history"
  );
}

export async function healthCheck() {
  return request<{
    status: string;
    model_loaded: boolean;
    timestamp: string;
  }>("/health");
}
