import axios from 'axios';

// Configure API base URL
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    // const token = await AsyncStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // No response received
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const patientAPI = {
  getCurrentPatient: () => apiClient.get('/api/patients/current'),
  getPatient: (patientId) => apiClient.get(`/api/patients/${patientId}`),
  listPatients: () => apiClient.get('/api/patients'),
  registerPatient: (data) => apiClient.post('/api/patients', data),
  updatePatient: (patientId, data) => apiClient.put(`/api/patients/${patientId}`, data),
};

export const predictionAPI = {
  predict: (patientId, readings) =>
    apiClient.post(`/api/patients/${patientId}/predict`, readings),
  getHistory: (patientId) =>
    apiClient.get(`/api/patients/${patientId}/predictions`),
};

export const alertAPI = {
  getAlerts: (patientId, limit = 10) =>
    apiClient.get(`/api/patients/${patientId}/alerts?limit=${limit}`),
  acknowledgeAlert: (alertId) =>
    apiClient.post(`/api/alerts/${alertId}/acknowledge`),
  getAllAlerts: () => apiClient.get('/api/alerts'),
};

export const sensorAPI = {
  submitReading: (patientId, reading) =>
    apiClient.post(`/api/patients/${patient_id}/readings`, reading),
  getReadings: (patientId, startDate, endDate) =>
    apiClient.get(`/api/patients/${patientId}/readings`, {
      params: { start_date: startDate, end_date: endDate },
    }),
};

export const analyticsAPI = {
  getStatistics: () => apiClient.get('/api/statistics'),
  getDashboard: () => apiClient.get('/api/dashboard'),
};

export default apiClient;