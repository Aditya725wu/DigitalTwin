import React, { useState } from 'react';
import { RefreshControl, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Badge, Button, Card, Paragraph, Title } from 'react-native-paper';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react-native';
import { alertAPI } from '../services/api';
import { useTwin } from '../context/AppContext';

const ago = (timestamp) => {
  const mins = Math.max(0, Math.floor((Date.now() - new Date(timestamp).getTime()) / 60000));
  return mins < 60 ? `${mins} min ago` : mins < 1440 ? `${Math.floor(mins / 60)} hours ago` : `${Math.floor(mins / 1440)} days ago`;
};

export default function AlertsScreenInteractive() {
  const { patientId, alerts, setAlerts, loading, refreshing, refresh, error, darkMode, notify } = useTwin();
  const [severity, setSeverity] = useState('ALL');
  const shown = alerts.filter((item) => severity === 'ALL' || item.severity === severity);
  const pending = alerts.filter((item) => !item.acknowledged).length;
  const acknowledge = async (alertId) => {
    try {
      const result = await alertAPI.acknowledgeAlert(alertId);
      setAlerts((items) => items.map((item) => item.alert_id === alertId ? result.data : item));
      notify('Alert acknowledged');
    } catch (requestError) { notify(requestError?.response?.data?.detail || 'Could not acknowledge alert.', 'error'); }
  };
  const color = darkMode ? '#f1f5f9' : '#172033';
  return <ScrollView style={[styles.container, darkMode && styles.darkBg]} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => refresh(true)} />}>
    <View style={styles.header}><View><Title style={{ color }}>Alerts</Title><Text style={styles.muted}>{pending} need acknowledgement · {patientId}</Text></View><Badge style={styles.badge}>{pending}</Badge></View>
    {error ? <Card style={styles.card}><Card.Content><Paragraph style={styles.error}>{error}</Paragraph><Button onPress={() => refresh(true)}>Retry</Button></Card.Content></Card> : null}
    {loading && !alerts.length ? <Text style={[styles.muted, { textAlign: 'center', margin: 16 }]}>Loading alerts…</Text> : null}
    <View style={styles.filters}>{['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((item) => <TouchableOpacity key={item} onPress={() => setSeverity(item)} style={[styles.filter, severity === item && styles.filterActive]}><Text style={[styles.filterText, severity === item && styles.filterTextActive]}>{item}</Text></TouchableOpacity>)}</View>
    {!shown.length ? <Card style={[styles.card, darkMode && styles.darkCard]}><Card.Content style={styles.empty}><CheckCircle size={36} color="#2e7d32" /><Title style={{ color }}>No alerts</Title><Text style={styles.muted}>No alerts match this severity filter.</Text></Card.Content></Card> : shown.map((alert) => {
      const tone = alert.severity === 'CRITICAL' ? '#d32f2f' : alert.severity === 'HIGH' ? '#ef6c00' : '#d18b00';
      return <Card key={alert.alert_id} style={[styles.card, alert.acknowledged && styles.acknowledged, darkMode && styles.darkCard]}><Card.Content>
        <View style={styles.alertTop}><AlertCircle size={21} color={tone} /><View style={{ flex: 1, marginLeft: 10 }}><Text style={{ color: tone, fontWeight: '800' }}>{alert.severity}</Text><View style={styles.time}><Clock size={12} color="#8893a2" /><Text style={styles.muted}> {ago(alert.timestamp)}</Text></View></View></View>
        <Text style={[styles.message, { color }]}>{alert.message}</Text>
        {!alert.acknowledged ? <Button mode="contained" onPress={() => void acknowledge(alert.alert_id)} style={styles.ackButton}>Acknowledge</Button> : <View style={styles.acknowledgedLabel}><CheckCircle size={15} color="#2e7d32" /><Text style={styles.green}> Acknowledged</Text></View>}
      </Card.Content></Card>;
    })}
    <Card style={[styles.card, darkMode && styles.darkCard]}><Card.Content><Title style={{ color }}>Alert summary</Title><View style={styles.summary}><SummaryItem label="Critical / High" value={alerts.filter((a) => ['CRITICAL','HIGH'].includes(a.severity)).length} color="#d32f2f" /><SummaryItem label="Medium" value={alerts.filter((a) => a.severity === 'MEDIUM').length} color="#d18b00" /><SummaryItem label="Acknowledged" value={alerts.filter((a) => a.acknowledged).length} color="#2e7d32" /></View></Card.Content></Card>
    <Text style={styles.disclaimer}>Synthetic demo data. Not a medical device. Not for clinical decisions.</Text>
  </ScrollView>;
}

function SummaryItem({ label, value, color }) { return <View style={styles.summaryItem}><Text style={[styles.summaryValue, { color }]}>{value}</Text><Text style={styles.muted}>{label}</Text></View>; }
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f4f7fb' }, darkBg: { backgroundColor: '#0b1220' }, darkCard: { backgroundColor: '#121c2e' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 }, badge: { backgroundColor: '#d32f2f', color: '#fff' }, muted: { color: '#778397', fontSize: 12 }, error: { color: '#b3261e' },
  filters: { flexDirection: 'row', flexWrap: 'wrap', gap: 7, marginHorizontal: 16, marginBottom: 12 }, filter: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 18, backgroundColor: '#e8edf4' }, filterActive: { backgroundColor: '#0b74de' }, filterText: { color: '#465365', fontWeight: '700', fontSize: 11 }, filterTextActive: { color: '#fff' },
  card: { marginHorizontal: 16, marginVertical: 6, elevation: 2 }, acknowledged: { opacity: 0.75 }, empty: { alignItems: 'center', gap: 7, paddingVertical: 20 }, alertTop: { flexDirection: 'row', alignItems: 'center' }, time: { flexDirection: 'row', alignItems: 'center', marginTop: 3 }, message: { fontSize: 15, lineHeight: 21, marginVertical: 14 }, ackButton: { backgroundColor: '#0b74de', alignSelf: 'flex-start' }, acknowledgedLabel: { flexDirection: 'row', alignItems: 'center' }, green: { color: '#2e7d32', fontSize: 12, fontWeight: '700' }, summary: { flexDirection: 'row', justifyContent: 'space-around', marginTop: 14 }, summaryItem: { alignItems: 'center' }, summaryValue: { fontWeight: '800', fontSize: 24 }, disclaimer: { color: '#778397', fontSize: 10, textAlign: 'center', margin: 18 },
});
