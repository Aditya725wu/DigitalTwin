import axios from 'axios';

export interface Patient {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  email: string;
  risk_level?: 'LOW' | 'MEDIUM' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  created_at: string;
  hypertension?: boolean;
  diabetes?: boolean;
  smoker?: boolean;
  total_cholesterol?: number;
  hdl_cholesterol?: number;
  ldl_cholesterol?: number;
}

export interface VitalSigns {
  heart_rate_bpm?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  oxygen_saturation?: number;
  ecg_rhythm?: string;
  ecg_quality?: string;
  timestamp: string;
  source?: string;
}

export interface CardiacPrediction {
  patient_id: string;
  cardiac_event_probability: number;
  arrhythmia_risk: string;
  blood_pressure_trend: string;
  bp_risk_level: string;
  risk_classification: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  framingham_score: number;
  recommended_actions: string[];
  timestamp: string;
}

export interface Alert {
  alert_id: string;
  patient_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  alert_type: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
  vital_signs?: Partial<VitalSigns>;
}

export interface Statistics {
  total_patients: number;
  high_risk_patients: number;
  total_alerts: number;
  critical_alerts: number;
  high_alerts: number;
  unacknowledged_alerts: number;
  average_heart_rate?: number;
  timestamp: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const patientAPI = {
  listPatients: () => apiClient.get<Patient[]>('/api/patients'),
  getPatient: (patientId: string) => apiClient.get<Patient>(`/api/patients/${patientId}`),
  registerPatient: (data: any) => apiClient.post<Patient>('/api/patients', data),
};

export const predictionAPI = {
  predictCardiac: (patientId: string) =>
    apiClient.post<CardiacPrediction>(`/api/patients/${patientId}/predict/cardiac`),
  getAlerts: (patientId: string) => apiClient.get<Alert[]>(`/api/patients/${patientId}/alerts`),
  getAllAlerts: () => apiClient.get<Alert[]>('/api/alerts'),
  acknowledgeAlert: (alertId: string) =>
    apiClient.post<Alert>(`/api/alerts/${alertId}/acknowledge`),
};

export const sensorAPI = {
  submitVitals: (patientId: string, vitals: VitalSigns) =>
    apiClient.post(`/api/patients/${patientId}/vitals`, vitals),
  getVitals: (patientId: string, limit = 100) =>
    apiClient.get<VitalSigns[]>(`/api/patients/${patientId}/vitals`, { params: { limit } }),
};

export const analyticsAPI = {
  getStatistics: () => apiClient.get<Statistics>('/api/statistics'),
};

export const healthAPI = {
  checkHealth: () => apiClient.get('/health'),
};

export default apiClient;
