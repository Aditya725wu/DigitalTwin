import React, { useEffect, useState } from 'react';
import { Alert, Modal, Pressable, ScrollView, Share, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Button, Card, Switch, TextInput, Title } from 'react-native-paper';
import { Check, Plus, Trash2 } from 'lucide-react-native';
import { API_BASE_URL, familyAPI, patientAPI } from '../services/api';
import { useTwin } from '../context/AppContext';

const dictionaries = {
  English: { ehr: 'Medical information', family: 'Family contact', reminders: 'Reminders', settings: 'Settings', emergency: 'Emergency card', signOut: 'Sign Out', about: 'About' },
  Hindi: { ehr: 'चिकित्सा जानकारी', family: 'परिवार संपर्क', reminders: 'रिमाइंडर', settings: 'सेटिंग्स', emergency: 'आपातकालीन कार्ड', signOut: 'साइन आउट', about: 'जानकारी' },
  Marathi: { ehr: 'वैद्यकीय माहिती', family: 'कुटुंब संपर्क', reminders: 'स्मरणपत्रे', settings: 'सेटिंग्ज', emergency: 'आपत्कालीन कार्ड', signOut: 'साइन आउट', about: 'माहिती' },
};

const toEhr = (patient) => ({
  name: patient?.name || '', age: patient?.age || 45, gender: patient?.gender || 'F', email: patient?.email || '', phone: patient?.phone || '',
  bmi: patient?.bmi || 24, height_cm: patient?.height_cm ?? null, weight_kg: patient?.weight_kg ?? null,
  smoker: Boolean(patient?.smoker), diabetes: Boolean(patient?.diabetes), hypertension: Boolean(patient?.hypertension),
  family_history_cvd: Boolean(patient?.family_history_cvd), family_history_hypertension: Boolean(patient?.family_history_hypertension),
  total_cholesterol: patient?.total_cholesterol ?? 200, hdl_cholesterol: patient?.hdl_cholesterol ?? 50,
  ldl_cholesterol: patient?.ldl_cholesterol ?? 120, medications: patient?.medications ?? [], medical_history: patient?.medical_history ?? [],
});

export default function ProfileScreenInteractive() {
  const { patient, patientId, family, setFamily, darkMode, setDarkMode, language, setLanguage, refresh, error, loading, notify, setPatientId, loadPatients } = useTwin();
  const [ehr, setEhr] = useState(toEhr(patient));
  const [contact, setContact] = useState({ name: '', phone: '' });
  const [reminders, setReminders] = useState([]);
  const [remindersLoaded, setRemindersLoaded] = useState(false);
  const [reminderTitle, setReminderTitle] = useState('');
  const [reminderType, setReminderType] = useState('Medication');
  const [emergencyOpen, setEmergencyOpen] = useState(false);
  const t = dictionaries[language] || dictionaries.English;
  const textColor = darkMode ? '#f1f5f9' : '#172033';
  const storageKey = `cardiotwin-reminders-${patientId}`;

  useEffect(() => { setEhr(toEhr(patient)); }, [patient]);
  useEffect(() => { setContact(family?.contact || { name: '', phone: '' }); }, [family]);
  useEffect(() => {
    setRemindersLoaded(false);
    AsyncStorage.getItem(storageKey).then((stored) => setReminders(stored ? JSON.parse(stored) : [])).catch(() => setReminders([])).finally(() => setRemindersLoaded(true));
  }, [storageKey]);
  useEffect(() => { if (remindersLoaded) AsyncStorage.setItem(storageKey, JSON.stringify(reminders)).catch(() => notify('Could not save reminders on this device.', 'error')); }, [storageKey, reminders, remindersLoaded]);

  const saveEhr = async () => {
    if (!ehr.name.trim()) return notify('Name is required.', 'error');
    if (Number(ehr.age) < 18 || Number(ehr.age) > 120) return notify('Age must be between 18 and 120.', 'error');
    try { await patientAPI.updatePatient(patientId, { ...ehr, age: Number(ehr.age), bmi: Number(ehr.bmi) }); await refresh(true); notify('Medical information saved'); }
    catch (saveError) { notify(saveError?.response?.data?.detail || 'Could not save medical information.', 'error'); }
  };

  const saveFamily = async () => {
    if (!contact.name.trim() || contact.phone.trim().length < 5) return notify('Enter a contact name and valid phone number.', 'error');
    try { const response = await familyAPI.save(patientId, contact); setFamily({ ...family, contact: response.data.contact }); notify('Family contact saved'); await refresh(true); }
    catch (saveError) { notify(saveError?.response?.data?.detail || 'Could not save family contact.', 'error'); }
  };

  const addReminder = () => {
    if (!reminderTitle.trim()) return notify('Enter a reminder name.', 'error');
    setReminders((items) => [{ id: `${Date.now()}`, title: reminderTitle.trim(), type: reminderType, done: false }, ...items]);
    setReminderTitle(''); notify(`${reminderType} reminder added`);
  };

  const deleteReminder = (id) => Alert.alert('Delete reminder?', 'This reminder will be removed from this device.', [
    { text: 'Cancel', style: 'cancel' }, { text: 'Delete', style: 'destructive', onPress: () => setReminders((items) => items.filter((item) => item.id !== id)) },
  ]);

  const signOut = () => Alert.alert('Sign out?', 'Return to the patient selector.', [
    { text: 'Cancel', style: 'cancel' }, { text: 'Sign Out', onPress: () => setPatientId(null) },
  ]);

  const shareEmergency = async () => {
    const conditions = [ehr.hypertension && 'Hypertension', ehr.diabetes && 'Diabetes', ehr.smoker && 'Smoking history', ...(ehr.medical_history || [])].filter(Boolean);
    const message = `CardioTwin emergency card (synthetic demo)\nPatient: ${patient?.name}\nKey conditions: ${conditions.join(', ') || 'None listed'}\nFamily contact: ${contact.name || 'Not set'} ${contact.phone || ''}`;
    try { await Share.share({ message }); } catch { notify('Could not open the share sheet.', 'error'); }
  };

  const retry = async () => { try { await loadPatients(); await refresh(true); notify('API connection restored'); } catch { notify('API is still unreachable. Check the URL under About.', 'error'); } };

  return <ScrollView style={[styles.container, darkMode && styles.darkBg]} contentContainerStyle={{ paddingBottom: 26 }}>
    {loading ? <Text style={styles.subtle}>Loading patient profile…</Text> : null}
    <Card style={[styles.card, darkMode && styles.darkCard]}><Card.Content><Title style={{ color: textColor }}>{patient?.name || 'Profile'}</Title><Text style={styles.subtle}>{patientId} · {patient?.email}</Text><Text style={styles.subtle}>Cardiovascular monitoring · Synthetic EHR</Text></Card.Content></Card>

    <Card style={[styles.card, darkMode && styles.darkCard]}><Card.Content><Title style={styles.section}>{t.ehr}</Title>
      {([['name','Name','default'],['age','Age','numeric'],['gender','Gender','default'],['email','Email','email-address'],['phone','Phone','phone-pad'],['bmi','BMI','decimal-pad'],['height_cm','Height cm','decimal-pad'],['weight_kg','Weight kg','decimal-pad'],['total_cholesterol','Total cholesterol','decimal-pad'],['hdl_cholesterol','HDL cholesterol','decimal-pad'],['ldl_cholesterol','LDL cholesterol','decimal-pad']]).map(([key,label,keyboardType]) => <TextInput key={key} mode="outlined" label={label} keyboardType={keyboardType} value={ehr[key] == null ? '' : String(ehr[key])} onChangeText={(value) => setEhr({ ...ehr, [key]: ['name','gender','email','phone'].includes(key) ? value : value === '' && ['height_cm','weight_kg'].includes(key) ? null : Number(value) })} style={styles.input} />)}
      <TextInput mode="outlined" label="Medications (comma separated)" value={(ehr.medications || []).join(', ')} onChangeText={(value) => setEhr({ ...ehr, medications: value.split(',').map((item) => item.trim()).filter(Boolean) })} style={styles.input} />
      <TextInput mode="outlined" label="Medical history (comma separated)" value={(ehr.medical_history || []).join(', ')} onChangeText={(value) => setEhr({ ...ehr, medical_history: value.split(',').map((item) => item.trim()).filter(Boolean) })} style={styles.input} />
      <View style={styles.switchRow}><Text style={{ color: textColor }}>Smoker</Text><Switch value={ehr.smoker} onValueChange={(value) => setEhr({ ...ehr, smoker: value })} /></View>
      <View style={styles.switchRow}><Text style={{ color: textColor }}>Diabetes</Text><Switch value={ehr.diabetes} onValueChange={(value) => setEhr({ ...ehr, diabetes: value })} /></View>
      <View style={styles.switchRow}><Text style={{ color: textColor }}>Hypertension</Text><Switch value={ehr.hypertension} onValueChange={(value) => setEhr({ ...ehr, hypertension: value })} /></View>
      <View style={styles.switchRow}><Text style={{ color: textColor }}>Family history of CVD</Text><Switch value={ehr.family_history_cvd} onValueChange={(value) => setEhr({ ...ehr, family_history_cvd: value })} /></View>
      <View style={styles.switchRow}><Text style={{ color: textColor }}>Family history of hypertension</Text><Switch value={ehr.family_history_hypertension} onValueChange={(value) => setEhr({ ...ehr, family_history_hypertension: value })} /></View>
      <Button mode="contained" onPress={() => void saveEhr()} style={styles.button}>Save medical information</Button>
    </Card.Content></Card>

    <Card style={[styles.card, darkMode && styles.darkCard]}><Card.Content><Title style={styles.section}>{t.family}</Title><TextInput mode="outlined" label="Contact name" value={contact.name} onChangeText={(name) => setContact({ ...contact, name })} style={styles.input} /><TextInput mode="outlined" label="Phone" keyboardType="phone-pad" value={contact.phone} onChangeText={(phone) => setContact({ ...contact, phone })} style={styles.input} /><Button mode="contained" onPress={() => void saveFamily()} style={styles.button}>Save family contact</Button><Text style={styles.subtle}>Flag streak: {family?.flag_streak ?? 0} of 3</Text>{family?.notifications?.map((item) => <Text key={item.notification_id} style={styles.subtle}>Simulated · {item.status.replaceAll('_',' ')} · {new Date(item.timestamp).toLocaleString()}</Text>)}</Card.Content></Card>

    <Card style={[styles.card, darkMode && styles.darkCard]}><Card.Content><Title style={styles.section}>{t.reminders}</Title><View style={styles.typeRow}>{['Medication','Appointment'].map((type) => <TouchableOpacity key={type} onPress={() => setReminderType(type)} style={[styles.typeChip, reminderType === type && styles.typeChipActive]}><Text style={reminderType === type ? styles.chipOn : styles.chipOff}>{type}</Text></TouchableOpacity>)}</View><TextInput mode="outlined" label={`${reminderType} reminder`} value={reminderTitle} onChangeText={setReminderTitle} style={styles.input} /><Button icon={() => <Plus size={16} color="#fff" />} mode="contained" onPress={addReminder} style={styles.button}>Add reminder</Button>{!reminders.length ? <Text style={styles.subtle}>No reminders yet.</Text> : null}{reminders.map((item) => <View key={item.id} style={styles.reminderRow}><TouchableOpacity onPress={() => setReminders((items) => items.map((row) => row.id === item.id ? { ...row, done: !row.done } : row))} style={styles.reminderCheck}>{item.done ? <Check size={17} color="#2e7d32" /> : <View style={styles.emptyCheck} />}</TouchableOpacity><View style={{ flex: 1 }}><Text style={[styles.reminderTitle, item.done && styles.done]}>{item.title}</Text><Text style={styles.subtle}>{item.type}</Text></View><TouchableOpacity onPress={() => deleteReminder(item.id)}><Trash2 size={18} color="#d32f2f" /></TouchableOpacity></View>)}</Card.Content></Card>

    <Card style={[styles.card, darkMode && styles.darkCard]}><Card.Content><Title style={styles.section}>{t.settings}</Title><View style={styles.switchRow}><View><Text style={{ color: textColor }}>Dark mode</Text><Text style={styles.subtle}>Applies across all app tabs</Text></View><Switch value={darkMode} onValueChange={(value) => setDarkMode(value)} /></View><Text style={styles.settingLabel}>Language</Text><View style={styles.typeRow}>{['English','Hindi','Marathi'].map((value) => <TouchableOpacity key={value} onPress={() => setLanguage(value)} style={[styles.typeChip, language === value && styles.typeChipActive]}><Text style={language === value ? styles.chipOn : styles.chipOff}>{value}</Text></TouchableOpacity>)}</View><Button mode="outlined" onPress={() => { setEmergencyOpen(true); void shareEmergency(); }} style={styles.button}>{t.emergency} · Share</Button></Card.Content></Card>

    <Card style={[styles.card, darkMode && styles.darkCard]}><Card.Content><Title style={styles.section}>{t.about}</Title><Text style={styles.subtle}>API base URL</Text><Text selectable style={styles.apiUrl}>{API_BASE_URL}</Text>{error ? <View><Text style={styles.error}>{error}</Text><Button onPress={() => void retry()}>Retry API connection</Button></View> : <Button onPress={() => void retry()}>Check API connection</Button>}</Card.Content></Card>
    <Button mode="outlined" textColor="#d32f2f" onPress={signOut} style={styles.signOut}>{t.signOut}</Button>
    <Text style={styles.disclaimer}>Synthetic demo data. Not a medical device. Not for clinical decisions.</Text>

    <Modal visible={emergencyOpen} transparent animationType="fade" onRequestClose={() => setEmergencyOpen(false)}><Pressable style={styles.overlay} onPress={() => setEmergencyOpen(false)}><View style={[styles.emergencyCard, darkMode && styles.darkCard]}><Title>{t.emergency}</Title><Text style={styles.emergencyText}>{patient?.name}</Text><Text style={styles.subtle}>Key conditions: {[ehr.hypertension && 'Hypertension',ehr.diabetes && 'Diabetes',ehr.smoker && 'Smoking history',...(ehr.medical_history || [])].filter(Boolean).join(', ') || 'None listed'}</Text><Text style={styles.subtle}>Family contact: {contact.name || 'Not set'} · {contact.phone || '—'}</Text><Button onPress={() => void shareEmergency()}>Share as text</Button><Button onPress={() => setEmergencyOpen(false)}>Close</Button></View></Pressable></Modal>
  </ScrollView>;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f4f7fb' }, darkBg: { backgroundColor: '#0b1220' }, darkCard: { backgroundColor: '#121c2e' },
  card: { margin: 16, marginTop: 10, elevation: 2 }, section: { color: '#0b74de', fontSize: 18 }, subtle: { color: '#738095', fontSize: 12, marginTop: 5 }, input: { marginTop: 8, backgroundColor: 'transparent' },
  switchRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', minHeight: 48, borderBottomWidth: 1, borderBottomColor: '#edf0f4' }, button: { marginTop: 12, backgroundColor: '#0b74de' }, settingLabel: { color: '#687386', marginTop: 14, marginBottom: 8 },
  typeRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginVertical: 8 }, typeChip: { borderRadius: 18, borderWidth: 1, borderColor: '#ccd5e1', paddingHorizontal: 12, paddingVertical: 8 }, typeChipActive: { backgroundColor: '#0b74de', borderColor: '#0b74de' }, chipOn: { color: '#fff', fontSize: 12, fontWeight: '700' }, chipOff: { color: '#526174', fontSize: 12, fontWeight: '700' },
  reminderRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#edf0f4', gap: 10 }, reminderCheck: { width: 26, height: 26, alignItems: 'center', justifyContent: 'center' }, emptyCheck: { width: 17, height: 17, borderWidth: 1, borderColor: '#aab5c4', borderRadius: 4 }, reminderTitle: { color: '#172033', fontWeight: '700' }, done: { textDecorationLine: 'line-through', color: '#7b8798' },
  apiUrl: { color: '#0b74de', marginTop: 5 }, error: { color: '#b3261e', marginTop: 8 }, signOut: { marginHorizontal: 16, borderColor: '#d32f2f' }, disclaimer: { color: '#778397', textAlign: 'center', fontSize: 10, margin: 18 }, overlay: { flex: 1, justifyContent: 'center', backgroundColor: '#0008', padding: 20 }, emergencyCard: { backgroundColor: '#fff', borderRadius: 18, padding: 20 }, emergencyText: { fontSize: 18, fontWeight: '700', marginVertical: 8 },
});
