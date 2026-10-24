import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { alertAPI, familyAPI, patientAPI, predictionAPI, sensorAPI, API_BASE_URL } from '../services/api';

const AppContext = createContext(null);
const DARK_KEY = 'cardiotwin-dark-mode';

export function AppProvider({ children }) {
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState(null);
  const [patient, setPatient] = useState(null);
  const [vitals, setVitals] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [baseline, setBaseline] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [family, setFamily] = useState(null);
  const [summary, setSummary] = useState(null);
  const [darkMode, setDarkModeState] = useState(false);
  const [language, setLanguage] = useState('English');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState(null);
  const noticeTimer = useRef(null);

  const notify = useCallback((message, kind = 'success') => {
    setNotice({ message, kind });
    if (noticeTimer.current) clearTimeout(noticeTimer.current);
    noticeTimer.current = setTimeout(() => setNotice(null), 2800);
  }, []);

  const loadPatients = useCallback(async () => {
    try {
      setError('');
      const response = await patientAPI.listPatients();
      setPatients(response.data || []);
      return response.data || [];
    } catch (loadError) {
      const message = loadError?.response?.data?.detail || 'CardioTwin API is unreachable. Check the API URL and retry.';
      setError(message);
      throw loadError;
    }
  }, []);

  const refresh = useCallback(async (manual = false) => {
    if (!patientId) return;
    if (manual) setRefreshing(true); else setLoading(true);
    setError('');
    try {
      const results = await Promise.all([
        patientAPI.getPatient(patientId), sensorAPI.getVitals(patientId, 100), predictionAPI.predictCardiac(patientId),
        alertAPI.getAlerts(patientId), sensorAPI.getBaseline(patientId), predictionAPI.explain(patientId),
        familyAPI.get(patientId), patientAPI.getSummary(patientId),
      ]);
      setPatient(results[0].data); setVitals(results[1].data || []); setPrediction(results[2].data);
      setAlerts(results[3].data || []); setBaseline(results[4].data); setExplanation(results[5].data);
      setFamily(results[6].data); setSummary(results[7].data);
    } catch (loadError) {
      const message = loadError?.response?.data?.detail || loadError?.message || 'Could not refresh patient data.';
      setError(message);
    } finally { setLoading(false); setRefreshing(false); }
  }, [patientId]);

  const setDarkMode = useCallback(async (value) => {
    setDarkModeState(value);
    try { await AsyncStorage.setItem(DARK_KEY, value ? 'true' : 'false'); } catch { /* Local preference is optional. */ }
  }, []);

  useEffect(() => {
    AsyncStorage.getItem(DARK_KEY).then((value) => setDarkModeState(value === 'true')).catch(() => {});
  }, []);

  useEffect(() => () => { if (noticeTimer.current) clearTimeout(noticeTimer.current); }, []);

  useEffect(() => {
    if (!patientId) return undefined;
    void refresh();
    const interval = setInterval(() => void refresh(true), 30000);
    return () => clearInterval(interval);
  }, [patientId, refresh]);

  useEffect(() => {
    if (!patientId) return undefined;
    let active = true;
    const socket = new WebSocket(`${API_BASE_URL.replace(/^http/, 'ws')}/ws/patient/${encodeURIComponent(patientId)}`);
    socket.onopen = () => socket.send(JSON.stringify({ type: 'subscribe' }));
    socket.onmessage = (event) => {
      if (!active) return;
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'vitals') setVitals((items) => [...items, message.data].slice(-100));
        if (message.type === 'alert') setAlerts((items) => [message.data, ...items]);
        if (message.type === 'prediction_update') setPrediction(message);
      } catch { /* Ignore malformed demo frames. */ }
    };
    socket.onerror = () => {};
    return () => { active = false; socket.close(); };
  }, [patientId]);

  const value = useMemo(() => ({
    patients, setPatients, patientId, setPatientId, patient, vitals, setVitals, alerts, setAlerts,
    prediction, setPrediction, baseline, explanation, family, setFamily, summary, darkMode, setDarkMode,
    language, setLanguage, loading, refreshing, error, refresh, loadPatients, notify, notice,
  }), [patients, patientId, patient, vitals, alerts, prediction, baseline, explanation, family, summary, darkMode, setDarkMode, language, loading, refreshing, error, refresh, loadPatients, notify, notice]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useTwin() {
  const value = useContext(AppContext);
  if (!value) throw new Error('useTwin must be used inside AppProvider');
  return value;
}
