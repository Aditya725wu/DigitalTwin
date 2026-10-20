import React, { useCallback, useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { Card, Paragraph, Title } from 'react-native-paper';
import { Activity, HeartPulse, TrendingDown, TrendingUp } from 'lucide-react-native';
import { sensorAPI } from '../services/api';

const PATIENT_ID = 'PAT000001';

export default function CardiacScreen() {
  const [vitals, setVitals] = useState([]);
  const [error, setError] = useState('');
  const loadVitals = useCallback(async () => {
    try { setError(''); setVitals((await sensorAPI.getVitals(PATIENT_ID, 24)).data || []); }
    catch (loadError) { setError('Telemetry history is unavailable.'); console.error(loadError); }
  }, []);
  useEffect(() => { void loadVitals(); }, [loadVitals]);
  const latest = vitals[vitals.length - 1];
  const previous = vitals[vitals.length - 2];
  const hrTrend = latest?.heart_rate_bpm > previous?.heart_rate_bpm ? 'rising' : 'stable';
  return <ScrollView style={styles.container}>
    <Card style={styles.card}><Card.Content>
      <View style={styles.heading}><HeartPulse size={24} color="#0b74de" /><Title style={styles.title}>Cardiac telemetry</Title></View>
      <Paragraph>Recent simulated wearable readings for the patient twin.</Paragraph>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <View style={styles.readingRow}><Reading label="Heart rate" value={latest?.heart_rate_bpm ? `${latest.heart_rate_bpm} bpm` : '—'} icon={hrTrend === 'rising' ? <TrendingUp size={18} color="#d32f2f" /> : <Activity size={18} color="#2e7d32" />} /><Reading label="Blood pressure" value={latest?.blood_pressure_systolic ? `${latest.blood_pressure_systolic}/${latest.blood_pressure_diastolic} mmHg` : '—'} /><Reading label="ECG rhythm" value={latest?.ecg_rhythm || '—'} /></View>
    </Card.Content></Card>
    <Card style={styles.card}><Card.Content><Title style={styles.title}>Recent readings</Title>{vitals.slice().reverse().map((reading, index) => <View key={`${reading.timestamp}-${index}`} style={styles.history}><Text style={styles.time}>{new Date(reading.timestamp).toLocaleTimeString()}</Text><Text style={styles.value}>{reading.heart_rate_bpm || '—'} bpm</Text><Text style={styles.bp}>{reading.blood_pressure_systolic ? `${reading.blood_pressure_systolic}/${reading.blood_pressure_diastolic}` : '—'}</Text></View>)}{!vitals.length && <Text style={styles.muted}>No telemetry has arrived yet.</Text>}</Card.Content></Card>
  </ScrollView>;
}
function Reading({ label, value, icon }) { return <View style={styles.reading}><View style={styles.icon}>{icon || <Activity size={18} color="#687386" />}</View><Text style={styles.label}>{label}</Text><Text style={styles.value}>{value}</Text></View>; }
const styles = StyleSheet.create({ container: { flex: 1, backgroundColor: '#f4f7fb' }, card: { margin: 16, marginTop: 6, elevation: 2 }, heading: { flexDirection: 'row', alignItems: 'center', gap: 10 }, title: { fontSize: 19, color: '#172033' }, readingRow: { marginTop: 18 }, reading: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#edf0f4' }, icon: { width: 28 }, label: { flex: 1, color: '#687386' }, value: { color: '#172033', fontWeight: '700' }, history: { flexDirection: 'row', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#edf0f4' }, time: { flex: 1, color: '#687386', fontSize: 12 }, value: { flex: 1, color: '#172033', fontWeight: '700' }, bp: { color: '#172033', fontWeight: '600' }, error: { color: '#b3261e', marginTop: 10 }, muted: { color: '#687386', marginTop: 16 } });
