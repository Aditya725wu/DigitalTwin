import React, { useState } from 'react';
import { Modal, Pressable, RefreshControl, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Card, Paragraph, ProgressBar, Title } from 'react-native-paper';
import { Activity, HeartPulse, ShieldAlert, Wind } from 'lucide-react-native';
import { useTwin } from '../context/AppContext';

export default function HomeScreen() {
  const { patient, patients, patientId, setPatientId, vitals, prediction, baseline, explanation, loading, refreshing, error, refresh, darkMode, notify } = useTwin();
  const [selectorVisible, setSelectorVisible] = useState(false);
  const vitalsLatest = vitals[vitals.length - 1];
  const risk = prediction?.risk_classification || patient?.risk_level || 'LOW';
  const probability = prediction?.cardiac_event_probability || 0;
  const riskColor = risk === 'CRITICAL' ? '#d32f2f' : risk === 'HIGH' ? '#ef6c00' : risk === 'MODERATE' ? '#f9a825' : '#2e7d32';
  const bg = darkMode ? '#0b1220' : '#f4f7fb';
  const text = darkMode ? '#f1f5f9' : '#172033';
  const muted = darkMode ? '#a9b4c4' : '#687386';
  return (
    <ScrollView style={[styles.container, { backgroundColor: bg }]} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => refresh(true)} tintColor={darkMode ? '#fff' : '#0b74de'} />}>
      <TouchableOpacity style={styles.selectorButton} onPress={() => setSelectorVisible(true)}><Text style={{ color: '#0b74de', fontWeight: '700' }}>Patient: {patient?.name || 'Select'} ⌄</Text><Text style={styles.small}>{patientId} · Change patient</Text></TouchableOpacity>
      <Card style={styles.hero}><Card.Content>
        <Text style={styles.eyebrow}>CARDIOTWIN PATIENT VIEW</Text>
        <Title style={[styles.title, { color: text }]}>{patient?.name || 'Synthetic patient'}</Title>
        <Paragraph>Personal cardiac status from EHR + wearable telemetry.</Paragraph>
        {loading ? <Text style={styles.muted}>Loading patient twin…</Text> : null}
        {error ? <View><Text style={styles.error}>{error}</Text><TouchableOpacity onPress={() => refresh(true)} style={styles.retry}><Text style={styles.retryText}>Retry</Text></TouchableOpacity></View> : null}
      </Card.Content></Card>

      <View style={styles.grid}>
        <Metric icon={<HeartPulse size={22} color="#0b74de" />} label="Heart rate" value={vitalsLatest?.heart_rate_bpm ? `${vitalsLatest.heart_rate_bpm} bpm` : '—'} darkMode={darkMode} />
        <Metric icon={<Activity size={22} color="#5e35b1" />} label="Blood pressure" value={vitalsLatest?.blood_pressure_systolic ? `${vitalsLatest.blood_pressure_systolic}/${vitalsLatest.blood_pressure_diastolic}` : '—'} darkMode={darkMode} />
        <Metric icon={<Wind size={22} color="#00897b" />} label="Oxygen" value={vitalsLatest?.oxygen_saturation ? `${vitalsLatest.oxygen_saturation}%` : '—'} darkMode={darkMode} />
        <Metric icon={<ShieldAlert size={22} color={riskColor} />} label="Twin risk" value={risk} color={riskColor} />
      </View>

      <Card style={styles.card}><Card.Content>
        <Title style={styles.sectionTitle}>Cardiac event forecast</Title>
        <Text style={[styles.probability, { color: riskColor }]}>{Math.round(probability * 100)}%</Text>
        <Text style={[styles.muted, { color: muted }]}>Estimated risk from the current synthetic EHR and recent wearable data.</Text>
        <ProgressBar progress={Math.min(probability, 1)} color={riskColor} style={styles.progress} />
        <Text style={[styles.rhythm, { color: text }]}>Rhythm: {prediction?.arrhythmia_risk || vitalsLatest?.ecg_rhythm || 'Awaiting telemetry'}</Text>
      </Card.Content></Card>

      <Card style={styles.card}><Card.Content><Title style={[styles.sectionTitle, { color: text }]}>Baseline deviation</Title><Text style={[styles.muted, { color: muted }]}>Average vs latest synthetic reading</Text>{baseline ? <View style={{ marginTop: 12 }}>{[['Heart rate','average_heart_rate_bpm','heart_rate_bpm','bpm'],['Systolic BP','average_systolic_bp','blood_pressure_systolic','mmHg'],['Diastolic BP','average_diastolic_bp','blood_pressure_diastolic','mmHg'],['SpO2','average_oxygen_saturation','oxygen_saturation','%']].map(([label, averageKey, latestKey, unit]) => { const deviation = baseline.deviation_percent?.[latestKey]; return <View key={label} style={styles.baselineRow}><Text style={{ color: muted, flex: 1 }}>{label}</Text><Text style={{ color: text, fontWeight: '700' }}>{baseline.average?.[averageKey] ?? '—'} → {baseline.latest?.[latestKey] ?? '—'} {unit}</Text><Text style={[styles.deviation, Math.abs(deviation || 0) >= 20 && styles.warning]}>{deviation == null ? '—' : `${deviation > 0 ? '+' : ''}${deviation}%`}</Text></View>; })}</View> : <Text style={styles.muted}>No baseline yet.</Text>}</Card.Content></Card>

      <Card style={styles.card}><Card.Content><Title style={[styles.sectionTitle, { color: text }]}>Why this risk score?</Title><Paragraph style={{ color: muted }}>Simplified scoring factors · {explanation?.total_points ?? '—'} / {explanation?.divisor ?? 45} points · {explanation?.final_class ?? risk}</Paragraph>{explanation?.factors?.map((factor) => <View key={factor.factor} style={styles.factorRow}><Text style={{ color: text, flex: 1 }}>{factor.factor}</Text><View style={styles.factorTrack}><View style={[styles.factorBar, { width: `${Math.max(5, factor.points / 45 * 100)}%` }]} /></View><Text style={{ color: text, width: 32, textAlign: 'right' }}>+{factor.points}</Text></View>)}</Card.Content></Card>
      <Text style={styles.disclaimer}>Synthetic demo data. Not a medical device. Not for clinical decisions.</Text>
      <Modal visible={selectorVisible} transparent animationType="fade" onRequestClose={() => setSelectorVisible(false)}><Pressable style={styles.overlay} onPress={() => setSelectorVisible(false)}><View style={[styles.modal, darkMode && styles.darkCard]}><Title style={{ color: text }}>Select patient</Title>{patients.map((item) => <TouchableOpacity key={item.patient_id} style={styles.patientRow} onPress={() => { setPatientId(item.patient_id); setSelectorVisible(false); notify(`Viewing ${item.name}`); }}><Text style={{ color: text, fontWeight: '700' }}>{item.name}</Text><Text style={styles.small}>{item.patient_id} · {item.age}</Text></TouchableOpacity>)}</View></Pressable></Modal>
    </ScrollView>
  );
}

function Metric({ icon, label, value, color = '#172033', darkMode }) {
  return <Card style={[styles.metric, darkMode && styles.darkCard]}><Card.Content><View style={styles.metricIcon}>{icon}</View><Text style={styles.metricLabel}>{label}</Text><Text style={[styles.metricValue, { color: darkMode ? '#f1f5f9' : color }]}>{value}</Text></Card.Content></Card>;
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
  selectorButton: { marginHorizontal: 16, marginTop: 12, padding: 13, borderRadius: 12, backgroundColor: '#eaf4ff' },
  small: { color: '#687386', fontSize: 11, marginTop: 4 },
  retry: { alignSelf: 'flex-start', marginTop: 8, backgroundColor: '#0b74de', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8 },
  retryText: { color: '#fff', fontWeight: '700' },
  baselineRow: { flexDirection: 'row', alignItems: 'center', gap: 5, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#edf0f4' },
  deviation: { color: '#687386', width: 54, textAlign: 'right', fontWeight: '700' }, warning: { color: '#d32f2f' },
  factorRow: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 8 }, factorTrack: { width: 90, height: 8, backgroundColor: '#e7edf5', borderRadius: 8, overflow: 'hidden' }, factorBar: { height: 8, backgroundColor: '#0b74de', borderRadius: 8 },
  disclaimer: { textAlign: 'center', color: '#778397', fontSize: 10, marginHorizontal: 18, marginBottom: 24 },
  overlay: { flex: 1, backgroundColor: '#0008', justifyContent: 'center', padding: 20 }, modal: { backgroundColor: '#fff', padding: 20, borderRadius: 18, maxHeight: '80%' }, patientRow: { padding: 14, borderBottomWidth: 1, borderBottomColor: '#edf0f4' }, darkCard: { backgroundColor: '#121c2e' },
});
