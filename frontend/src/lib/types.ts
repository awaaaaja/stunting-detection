export interface ShapFeature {
  feature: string;
  value: number;
  shap_value: number;
  abs_shap: number;
  contribution_pct: number;
}

export interface ShapPerClass {
  base_value: number;
  features: ShapFeature[];
}

export interface Prediction {
  class: string;
  class_id: number;
  risk_level: string;
  risk_score: number;
  probabilities: Record<string, number>;
}

export interface Source {
  source: string;
  page: number;
}

export interface Rekomendasi {
  answer: string;
  sources: Source[];
}

export interface PredictResponse {
  prediction: Prediction;
  shap: ShapPerClass;
  shap_per_class: Record<string, ShapPerClass>;
  rekomendasi: Rekomendasi;
  timestamp: string;
  usia_bulan: number;
  jenis_kelamin: string;
  tinggi_cm: number;
  balita_id?: string;
}

export interface HistoryRecord {
  timestamp: string;
  usia_bulan: number;
  jenis_kelamin: string;
  tinggi_cm: number;
  prediction: Prediction;
  shap: ShapPerClass;
}

export interface BalitaHistory {
  balita_id: string;
  records: HistoryRecord[];
}

export interface HistorySummary {
  balita_id: string;
  total_records: number;
  last_prediction: string | null;
  last_checked: string | null;
}

export interface PredictInput {
  usia_bulan: number;
  jenis_kelamin: string;
  tinggi_cm: number;
  balita_id?: string;
}
