import { create } from 'zustand';

export interface Patient {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  email: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  last_glucose: number;
  glucose_trend: number;
}

export interface Alert {
  alert_id: string;
  patient_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

interface DashboardStore {
  patients: Patient[];
  alerts: Alert[];
  selectedPatient: Patient | null;
  isLoading: boolean;

  setPatients: (patients: Patient[]) => void;
  setAlerts: (alerts: Alert[]) => void;
  setSelectedPatient: (patient: Patient | null) => void;
  setIsLoading: (loading: boolean) => void;
  addAlert: (alert: Alert) => void;
  acknowledgeAlert: (alertId: string) => void;
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  patients: [],
  alerts: [],
  selectedPatient: null,
  isLoading: false,

  setPatients: (patients) => set({ patients }),
  setAlerts: (alerts) => set({ alerts }),
  setSelectedPatient: (patient) => set({ selectedPatient: patient }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts],
    })),
  acknowledgeAlert: (alertId) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.alert_id === alertId ? { ...a, acknowledged: true } : a
      ),
    })),
}));
