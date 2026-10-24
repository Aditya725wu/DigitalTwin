import React, { useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { MD3DarkTheme, MD3LightTheme, PaperProvider } from 'react-native-paper';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { AppProvider, useTwin } from './src/context/AppContext';
import { API_BASE_URL } from './src/services/api';

// Import screens
import HomeScreen from './src/screens/HomeScreen';
import CardiacScreen from './src/screens/CardiacScreen';
import AlertsScreen from './src/screens/AlertsScreenInteractive';
import ProfileScreen from './src/screens/ProfileScreenInteractive';

const Tab = createBottomTabNavigator();

function PatientSelector() {
  const { patients, setPatients, setPatientId, loadPatients, error, setLanguage, darkMode } = useTwin();
  const [busy, setBusy] = useState(false);
  const [localError, setLocalError] = useState('');
  const load = async () => {
    setBusy(true); setLocalError('');
    try { const data = await loadPatients(); setPatients(data); }
    catch (requestError) { setLocalError(requestError?.response?.data?.detail || 'Could not reach the API.'); }
    finally { setBusy(false); }
  };
  useEffect(() => { if (!patients.length) void load(); }, []);
  return <View style={[styles.selector, darkMode && styles.darkBg]}>
    <Text style={[styles.brand, darkMode && styles.lightText]}>CardioTwin</Text>
    <Text style={[styles.subtitle, darkMode && styles.mutedLight]}>Choose a synthetic demo patient</Text>
    {(localError || error) ? <View><Text style={styles.error}>{localError || error}</Text><TouchableOpacity onPress={() => void load()} style={styles.primaryButton}><Text style={styles.buttonText}>Retry API connection</Text></TouchableOpacity><Text style={styles.small}>{API_BASE_URL}</Text></View> : null}
    {busy ? <ActivityIndicator size="large" color="#0b74de" /> : null}
    {!busy && !patients.length && !localError && <TouchableOpacity onPress={() => void load()} style={styles.primaryButton}><Text style={styles.buttonText}>Load patients</Text></TouchableOpacity>}
    <FlatList data={patients} keyExtractor={(item) => item.patient_id} contentContainerStyle={{ width: '100%', paddingTop: 18 }} renderItem={({ item }) => <TouchableOpacity onPress={() => setPatientId(item.patient_id)} style={[styles.patientChoice, darkMode && styles.darkCard]}><View><Text style={[styles.patientName, darkMode && styles.lightText]}>{item.name}</Text><Text style={styles.small}>{item.patient_id} · {item.age} years</Text></View><Text style={styles.riskText}>{item.risk_level || 'LOW'}</Text></TouchableOpacity>} />
    <Text style={styles.disclaimer}>Synthetic demo data. Not a medical device. Not for clinical decisions.</Text>
  </View>;
}

function Tabs() {
  const { darkMode } = useTwin();
  return <NavigationContainer>
    <Tab.Navigator screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        const names = { Home: focused ? 'home' : 'home-outline', Cardiac: focused ? 'heart-pulse' : 'heart-outline', Alerts: focused ? 'bell' : 'bell-outline', Profile: focused ? 'account' : 'account-outline' };
        return <MaterialCommunityIcons name={names[route.name]} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#0b74de', tabBarInactiveTintColor: darkMode ? '#a9b4c4' : 'gray',
      tabBarStyle: { backgroundColor: darkMode ? '#121c2e' : '#fff' },
      headerShown: true, headerStyle: { backgroundColor: darkMode ? '#121c2e' : '#0066cc' },
      headerTintColor: darkMode ? '#fff' : '#fff',
    })}>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Cardiac" component={CardiacScreen} />
      <Tab.Screen name="Alerts" component={AlertsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  </NavigationContainer>;
}

function AppShell() {
  const { patientId, darkMode, notice } = useTwin();
  return <PaperProvider theme={darkMode ? MD3DarkTheme : MD3LightTheme}><View style={{ flex: 1 }}>{patientId ? <Tabs /> : <PatientSelector />}{notice ? <View pointerEvents="none" style={[styles.toast, notice.kind === 'error' && styles.toastError]}><Text style={styles.toastText}>{notice.message}</Text></View> : null}</View></PaperProvider>;
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AppProvider><AppShell /></AppProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  selector: { flex: 1, backgroundColor: '#f4f7fb', alignItems: 'center', paddingHorizontal: 20, paddingTop: 70 },
  darkBg: { backgroundColor: '#0b1220' }, darkCard: { backgroundColor: '#121c2e' },
  brand: { color: '#0b74de', fontSize: 34, fontWeight: '800' }, subtitle: { color: '#687386', marginTop: 8 },
  patientChoice: { width: '100%', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16, marginBottom: 10, backgroundColor: '#fff', borderRadius: 14, elevation: 1 },
  patientName: { color: '#172033', fontSize: 16, fontWeight: '700' }, small: { color: '#687386', fontSize: 12, marginTop: 5 }, riskText: { color: '#0b74de', fontSize: 11, fontWeight: '800' },
  primaryButton: { marginTop: 14, backgroundColor: '#0b74de', borderRadius: 10, paddingHorizontal: 16, paddingVertical: 11 }, buttonText: { color: '#fff', fontWeight: '700' },
  error: { color: '#b3261e', marginTop: 18, textAlign: 'center' }, disclaimer: { color: '#778397', fontSize: 10, textAlign: 'center', marginVertical: 18 }, lightText: { color: '#f1f5f9' }, mutedLight: { color: '#a9b4c4' },
  toast: { position: 'absolute', top: 56, alignSelf: 'center', maxWidth: '90%', backgroundColor: '#138a52', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 11, elevation: 10, zIndex: 100 }, toastError: { backgroundColor: '#bb2f35' }, toastText: { color: '#fff', fontWeight: '700', textAlign: 'center' },
});
