import axios from 'axios';

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
const apiClient = axios.create({ baseURL: API_BASE_URL, headers: { 'Content-Type': 'application/json' }, timeout: 10000 });
const path = (id) => encodeURIComponent(id);

export const patientAPI = {
  getPatient: (id) => apiClient.get(`/api/patients/${path(id)}`),
  listPatients: () => apiClient.get('/api/patients'),
  registerPatient: (data) => apiClient.post('/api/patients', data),
  updatePatient: (id, data) => apiClient.put(`/api/patients/${path(id)}`, data),
  deletePatient: (id) => apiClient.delete(`/api/patients/${path(id)}`),
  getSummary: (id) => apiClient.get(`/api/patients/${path(id)}/summary`),
  exportPatient: (id) => apiClient.get(`/api/patients/${path(id)}/export`),
  resetDemo: () => apiClient.post('/api/reset'),
};

export const predictionAPI = {
  predictCardiac: (id) => apiClient.post(`/api/patients/${path(id)}/predict/cardiac`),
  whatIf: (id, values) => apiClient.post(`/api/patients/${path(id)}/whatif`, values),
  explain: (id) => apiClient.get(`/api/patients/${path(id)}/explain`),
};

export const alertAPI = {
  getAlerts: (id, limit = 100) => apiClient.get(`/api/patients/${path(id)}/alerts`, { params: { limit } }),
  acknowledgeAlert: (id) => apiClient.post(`/api/alerts/${path(id)}/acknowledge`),
  getAllAlerts: () => apiClient.get('/api/alerts'),
};

export const sensorAPI = {
  submitVitals: (id, reading) => apiClient.post(`/api/patients/${path(id)}/vitals`, reading),
  getVitals: (id, limit = 100) => apiClient.get(`/api/patients/${path(id)}/vitals`, { params: { limit } }),
  getBaseline: (id) => apiClient.get(`/api/patients/${path(id)}/baseline`),
};

export const familyAPI = {
  get: (id) => apiClient.get(`/api/patients/${path(id)}/family-contact`),
  save: (id, contact) => apiClient.post(`/api/patients/${path(id)}/family-contact`, contact),
};

export const simulationAPI = {
  start: (id) => apiClient.post(`/api/simulate/${path(id)}/start`),
  stop: (id) => apiClient.post(`/api/simulate/${path(id)}/stop`),
};

export const analyticsAPI = { getStatistics: () => apiClient.get('/api/statistics') };
export default apiClient;
