import axios from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

export const patientAPI = {
  getCurrentPatient: () => apiClient.get('/api/patients/PAT000001'),
  getPatient: (patientId) => apiClient.get(`/api/patients/${patientId}`),
  listPatients: () => apiClient.get('/api/patients'),
  registerPatient: (data) => apiClient.post('/api/patients', data),
};

export const predictionAPI = {
  predictCardiac: (patientId) => apiClient.post(`/api/patients/${patientId}/predict/cardiac`),
  predict: (patientId, readings) => apiClient.post(`/api/patients/${patientId}/predict`, readings),
};

export const alertAPI = {
  getAlerts: (patientId, limit = 10) => apiClient.get(`/api/patients/${patientId}/alerts`, { params: { limit } }),
  acknowledgeAlert: (alertId) => apiClient.post(`/api/alerts/${alertId}/acknowledge`),
  getAllAlerts: () => apiClient.get('/api/alerts'),
};

export const sensorAPI = {
  submitVitals: (patientId, reading) => apiClient.post(`/api/patients/${patientId}/vitals`, reading),
  getVitals: (patientId, limit = 24) => apiClient.get(`/api/patients/${patientId}/vitals`, { params: { limit } }),
};

export const analyticsAPI = {
  getStatistics: () => apiClient.get('/api/statistics'),
};

export default apiClient;
