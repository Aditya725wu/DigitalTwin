import { create } from 'zustand';
import type { Alert, Patient } from '@/lib/api';

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
  addAlert: (alert) => set((state) => ({ alerts: [alert, ...state.alerts] })),
  acknowledgeAlert: (alertId) =>
    set((state) => ({
      alerts: state.alerts.map((alert) =>
        alert.alert_id === alertId ? { ...alert, acknowledged: true } : alert,
      ),
    })),
}));
