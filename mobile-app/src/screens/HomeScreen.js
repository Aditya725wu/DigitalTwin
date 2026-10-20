import React, { useCallback, useEffect, useState } from 'react';
import { RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { Card, Paragraph, ProgressBar, Title } from 'react-native-paper';
import { Activity, HeartPulse, ShieldAlert, Wind } from 'lucide-react-native';
import { patientAPI, predictionAPI, sensorAPI } from '../services/api';

const PATIENT_ID = 'PAT000001';

export default function HomeScreen() {
  const [patient, setPatient] = useState(null);
  const [vitals, setVitals] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const loadData = useCallback(async () => {
    try {
      setError('');
      const [patientResult, vitalsResult, predictionResult] = await Promise.all([
        patientAPI.getPatient(PATIENT_ID),
        sensorAPI.getVitals(PATIENT_ID, 1),
        predictionAPI.predictCardiac(PATIENT_ID),
      ]);
      setPatient(patientResult.data);
      setVitals(vitalsResult.data?.[0] || null);
      setPrediction(predictionResult.data);
    } catch (loadError) {
      setError('Connect the backend to load the latest cardiac twin.');
      console.error(loadError);
    }
  }, []);

  useEffect(() => { void loadData(); }, [loadData]);

  const refresh = async () => { setRefreshing(true); await loadData(); setRefreshing(false); };
  const risk = prediction?.risk_classification || patient?.risk_level || 'LOW';
  const probability = prediction?.cardiac_event_probability || 0;
  const riskColor = risk === 'CRITICAL' ? '#d32f2f' : risk === 'HIGH' ? '#ef6c00' : risk === 'MODERATE' ? '#f9a825' : '#2e7d32';

  return (
    <ScrollView style={styles.container} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} />}>
      <Card style={styles.hero}><Card.Content>
        <Text style={styles.eyebrow}>CARDIOTWIN PATIENT VIEW</Text>
        <Title style={styles.title}>{patient?.name || 'Synthetic patient'}</Title>
        <Paragraph>Personal cardiac status from EHR + wearable telemetry.</Paragraph>
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </Card.Content></Card>

      <View style={styles.grid}>
        <Metric icon={<HeartPulse size={22} color="#0b74de" />} label="Heart rate" value={vitals?.heart_rate_bpm ? `${vitals.heart_rate_bpm} bpm` : '—'} />
        <Metric icon={<Activity size={22} color="#5e35b1" />} label="Blood pressure" value={vitals?.blood_pressure_systolic ? `${vitals.blood_pressure_systolic}/${vitals.blood_pressure_diastolic}` : '—'} />
        <Metric icon={<Wind size={22} color="#00897b" />} label="Oxygen" value={vitals?.oxygen_saturation ? `${vitals.oxygen_saturation}%` : '—'} />
        <Metric icon={<ShieldAlert size={22} color={riskColor} />} label="Twin risk" value={risk} color={riskColor} />
      </View>

      <Card style={styles.card}><Card.Content>
        <Title style={styles.sectionTitle}>Cardiac event forecast</Title>
        <Text style={[styles.probability, { color: riskColor }]}>{Math.round(probability * 100)}%</Text>
        <Text style={styles.muted}>Estimated risk from the current synthetic EHR and recent wearable data.</Text>
        <ProgressBar progress={Math.min(probability, 1)} color={riskColor} style={styles.progress} />
        <Text style={styles.rhythm}>Rhythm: {prediction?.arrhythmia_risk || vitals?.ecg_rhythm || 'Awaiting telemetry'}</Text>
      </Card.Content></Card>
    </ScrollView>
  );
}

function Metric({ icon, label, value, color = '#172033' }) {
  return <Card style={styles.metric}><Card.Content><View style={styles.metricIcon}>{icon}</View><Text style={styles.metricLabel}>{label}</Text><Text style={[styles.metricValue, { color }]}>{value}</Text></Card.Content></Card>;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f4f7fb' },
  hero: { margin: 16, marginBottom: 10, elevation: 2 },
  eyebrow: { color: '#0b74de', fontSize: 11, fontWeight: '700', letterSpacing: 1.2 },
  title: { color: '#172033', fontSize: 26, marginTop: 6 },
  error: { color: '#b3261e', marginTop: 10 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', paddingHorizontal: 12 },
  metric: { width: '48%', marginBottom: 10, elevation: 1 },
  metricIcon: { marginBottom: 8 },
  metricLabel: { color: '#687386', fontSize: 12 },
  metricValue: { fontSize: 20, fontWeight: '700', marginTop: 4 },
  card: { margin: 16, marginTop: 6, elevation: 2 },
  sectionTitle: { fontSize: 18, color: '#172033' },
  probability: { fontSize: 48, fontWeight: '800', marginTop: 12 },
  muted: { color: '#687386', lineHeight: 20 },
  progress: { height: 10, borderRadius: 6, marginVertical: 16 },
  rhythm: { color: '#172033', fontWeight: '600' },
});
