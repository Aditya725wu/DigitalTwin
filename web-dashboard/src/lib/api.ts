import axios from 'axios';

export type RiskClass = 'LOW' | 'MODERATE' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Patient {
  patient_id: string; name: string; age: number; gender: string; email: string; phone: string;
  bmi: number; height_cm?: number | null; weight_kg?: number | null;
  smoker?: boolean; diabetes?: boolean; hypertension?: boolean; family_history_cvd?: boolean;
  family_history_hypertension?: boolean; total_cholesterol?: number; hdl_cholesterol?: number;
  ldl_cholesterol?: number; medications?: string[]; medical_history?: string[];
  risk_level?: RiskClass; created_at: string;
}

export type PatientInput = Omit<Patient, 'patient_id' | 'created_at' | 'risk_level'>;

export interface VitalSigns {
  heart_rate_bpm?: number | null; blood_pressure_systolic?: number | null;
  blood_pressure_diastolic?: number | null; oxygen_saturation?: number | null;
  ecg_rhythm?: string | null; ecg_quality?: string | null; timestamp?: string; source?: string;
}

export interface CardiacPrediction {
  patient_id: string; cardiac_event_probability: number; arrhythmia_risk: string;
  blood_pressure_trend: string; bp_risk_level: string; risk_classification: RiskClass;
  framingham_score: number; recommended_actions: string[]; timestamp: string;
}

export interface Alert {
  alert_id: string; patient_id: string; severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  alert_type: string; message: string; timestamp: string; acknowledged: boolean;
  vital_signs?: Partial<VitalSigns>;
}

export interface Statistics {
  total_patients: number; high_risk_patients: number; total_alerts: number;
  critical_alerts: number; high_alerts: number; unacknowledged_alerts: number;
  average_heart_rate?: number; timestamp: string;
}

export interface Baseline {
  patient_id: string; reading_count: number;
  average: Record<string, number | null>; latest: VitalSigns | null;
  deviation_percent: Record<string, number | null>; large_deviation: boolean;
}

export interface RiskExplanation {
  patient_id: string; factors: Array<{ factor: string; points: number }>;
  total_points: number; divisor: number; probability: number; final_class: RiskClass;
  active_scoring_class: RiskClass;
}

export interface FamilyData {
  patient_id: string; contact: { name: string; phone: string } | null;
  notifications: Array<{ notification_id: string; message: string; status: string; simulated: boolean; timestamp: string }>;
  flag_streak: number;
}

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10_000,
});

export const patientAPI = {
  listPatients: () => apiClient.get<Patient[]>('/api/patients'),
  getPatient: (id: string) => apiClient.get<Patient>(`/api/patients/${encodeURIComponent(id)}`),
  registerPatient: (data: PatientInput) => apiClient.post<Patient>('/api/patients', data),
  updatePatient: (id: string, data: PatientInput) => apiClient.put<Patient>(`/api/patients/${encodeURIComponent(id)}`, data),
  deletePatient: (id: string) => apiClient.delete(`/api/patients/${encodeURIComponent(id)}`),
  exportPatient: (id: string) => apiClient.get(`/api/patients/${encodeURIComponent(id)}/export`),
  resetDemo: () => apiClient.post('/api/reset'),
  getSummary: (id: string) => apiClient.get<{ summary: string }>(`/api/patients/${encodeURIComponent(id)}/summary`),
};

export const predictionAPI = {
  predictCardiac: (id: string) => apiClient.post<CardiacPrediction>(`/api/patients/${encodeURIComponent(id)}/predict/cardiac`),
  whatIf: (id: string, values: Partial<PatientInput & VitalSigns>) => apiClient.post<CardiacPrediction & { what_if_only: boolean; history_unchanged: boolean }>(`/api/patients/${encodeURIComponent(id)}/whatif`, values),
  explain: (id: string) => apiClient.get<RiskExplanation>(`/api/patients/${encodeURIComponent(id)}/explain`),
  getAlerts: (id: string) => apiClient.get<Alert[]>(`/api/patients/${encodeURIComponent(id)}/alerts`),
  getAllAlerts: () => apiClient.get<Alert[]>('/api/alerts'),
  acknowledgeAlert: (id: string) => apiClient.post<Alert>(`/api/alerts/${encodeURIComponent(id)}/acknowledge`),
};

export const sensorAPI = {
  submitVitals: (id: string, vitals: VitalSigns) => apiClient.post(`/api/patients/${encodeURIComponent(id)}/vitals`, vitals),
  getVitals: (id: string, limit = 100) => apiClient.get<VitalSigns[]>(`/api/patients/${encodeURIComponent(id)}/vitals`, { params: { limit } }),
  getBaseline: (id: string) => apiClient.get<Baseline>(`/api/patients/${encodeURIComponent(id)}/baseline`),
};

export const familyAPI = {
  get: (id: string) => apiClient.get<FamilyData>(`/api/patients/${encodeURIComponent(id)}/family-contact`),
  save: (id: string, contact: { name: string; phone: string }) => apiClient.post(`/api/patients/${encodeURIComponent(id)}/family-contact`, contact),
};

export const simulationAPI = {
  start: (id: string) => apiClient.post(`/api/simulate/${encodeURIComponent(id)}/start`),
  stop: (id: string) => apiClient.post(`/api/simulate/${encodeURIComponent(id)}/stop`),
};

export const analyticsAPI = { getStatistics: () => apiClient.get<Statistics>('/api/statistics') };
export const healthAPI = { checkHealth: () => apiClient.get('/health') };

export function patientSocketUrl(id: string) {
  return `${API_URL.replace(/^http/, 'ws')}/ws/patient/${encodeURIComponent(id)}`;
}

export default apiClient;
