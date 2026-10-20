'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  HeartPulse,
  RefreshCw,
  ShieldAlert,
  Wind,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import toast from 'react-hot-toast';
import {
  Alert,
  CardiacPrediction,
  Statistics,
  VitalSigns,
  analyticsAPI,
  patientAPI,
  predictionAPI,
  sensorAPI,
} from '@/lib/api';
import { useDashboardStore } from '@/store/dashboard';

const RISK_COLORS = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
};

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return Number.isNaN(date.getTime())
    ? '—'
    : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const formatDateTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return Number.isNaN(date.getTime())
    ? 'Unknown time'
    : date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
};

const riskBadge = (risk?: string) => {
  switch (risk) {
    case 'CRITICAL':
      return 'bg-red-100 text-red-700 ring-red-200';
    case 'HIGH':
      return 'bg-orange-100 text-orange-700 ring-orange-200';
    case 'MEDIUM':
    case 'MODERATE':
      return 'bg-amber-100 text-amber-700 ring-amber-200';
    default:
      return 'bg-emerald-100 text-emerald-700 ring-emerald-200';
  }
};

function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
  tone,
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof Activity;
  tone: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</p>
          <p className="mt-3 text-3xl font-bold tracking-tight text-slate-950">{value}</p>
          <p className="mt-2 text-sm text-slate-500">{detail}</p>
        </div>
        <span className={`rounded-xl p-3 ${tone}`}>
          <Icon className="h-5 w-5" />
        </span>
      </div>
    </div>
  );
}

function LoadingCard({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-2xl border border-slate-200 bg-white p-6 shadow-sm ${className}`} />;
}

export default function Dashboard() {
  const { patients, alerts, setPatients, setAlerts, acknowledgeAlert } = useDashboardStore();
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [vitalsByPatient, setVitalsByPatient] = useState<Record<string, VitalSigns[]>>({});
  const [predictions, setPredictions] = useState<Record<string, CardiacPrediction>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dataWarning, setDataWarning] = useState<string | null>(null);

  const loadDashboardData = useCallback(async (refresh = false) => {
    setIsLoading(!refresh);
    setIsRefreshing(refresh);
    setError(null);
    setDataWarning(null);

    try {
      const [patientsResult, statsResult, alertsResult] = await Promise.allSettled([
        patientAPI.listPatients(),
        analyticsAPI.getStatistics(),
        predictionAPI.getAllAlerts(),
      ]);

      if (patientsResult.status === 'rejected') {
        throw new Error('Unable to reach the cardiac patient service.');
      }

      const loadedPatients = patientsResult.value.data ?? [];
      setPatients(loadedPatients);
      if (statsResult.status === 'fulfilled') setStatistics(statsResult.value.data);
      if (alertsResult.status === 'fulfilled') setAlerts(alertsResult.value.data ?? []);

      const telemetryResults = await Promise.all(
        loadedPatients.map(async (patient) => {
          const [vitalsResult, predictionResult] = await Promise.allSettled([
            sensorAPI.getVitals(patient.patient_id, 24),
            predictionAPI.predictCardiac(patient.patient_id),
          ]);
          return {
            patientId: patient.patient_id,
            vitals: vitalsResult.status === 'fulfilled' ? vitalsResult.value.data ?? [] : [],
            prediction: predictionResult.status === 'fulfilled' ? predictionResult.value.data : null,
            failed: vitalsResult.status === 'rejected' || predictionResult.status === 'rejected',
          };
        }),
      );

      setVitalsByPatient(Object.fromEntries(telemetryResults.map((item) => [item.patientId, item.vitals])));
      setPredictions(
        Object.fromEntries(
          telemetryResults
            .filter((item) => Boolean(item.prediction))
            .map((item) => [item.patientId, item.prediction as CardiacPrediction]),
        ),
      );

      const partialFailures =
        statsResult.status === 'rejected' ||
        alertsResult.status === 'rejected' ||
        telemetryResults.some((item) => item.failed);
      if (partialFailures) {
        setDataWarning('Some cardiac telemetry is unavailable. Showing the latest data received.');
      }
    } catch (loadError) {
      const message = loadError instanceof Error ? loadError.message : 'Unable to load the dashboard.';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [setAlerts, setPatients]);

  useEffect(() => {
    void loadDashboardData();
    const interval = window.setInterval(() => void loadDashboardData(true), 30000);
    return () => window.clearInterval(interval);
  }, [loadDashboardData]);

  const patientNames = useMemo(
    () => Object.fromEntries(patients.map((patient) => [patient.patient_id, patient.name])),
    [patients],
  );

  const trendData = useMemo(() => {
    return Object.values(vitalsByPatient)
      .flat()
      .filter((vital) => vital.timestamp)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .slice(-24)
      .map((vital) => ({
        time: formatTime(vital.timestamp),
        heartRate: vital.heart_rate_bpm ?? null,
        systolic: vital.blood_pressure_systolic ?? null,
      }));
  }, [vitalsByPatient]);

  const latestVitals = useMemo(
    () => Object.values(vitalsByPatient).map((vitals) => vitals[vitals.length - 1]).filter(Boolean),
    [vitalsByPatient],
  );
  const heartRateReadings = latestVitals.filter((vital) => vital.heart_rate_bpm != null);
  const oxygenReadings = latestVitals.filter((vital) => vital.oxygen_saturation != null);
  const averageHeartRate = heartRateReadings.length
    ? Math.round(heartRateReadings.reduce((sum, vital) => sum + (vital.heart_rate_bpm ?? 0), 0) / heartRateReadings.length)
    : null;
  const averageOxygen = oxygenReadings.length
    ? (oxygenReadings.reduce((sum, vital) => sum + (vital.oxygen_saturation ?? 0), 0) / oxygenReadings.length).toFixed(1)
    : null;

  const riskDistribution = (['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] as const).map((risk) => ({
    name: risk,
    value: patients.filter((patient) => {
      const normalizedRisk = patient.risk_level === 'MODERATE' ? 'MEDIUM' : patient.risk_level;
      return normalizedRisk === risk;
    }).length,
    color: RISK_COLORS[risk],
  }));

  const predictionRows = patients
    .map((patient) => ({ patient, prediction: predictions[patient.patient_id] }))
    .filter((row) => row.prediction)
    .sort((a, b) => b.prediction!.cardiac_event_probability - a.prediction!.cardiac_event_probability);

  const activeAlerts = alerts.filter((alert) => !alert.acknowledged).length;
  const highRiskCount = statistics?.high_risk_patients ?? patients.filter((patient) => ['HIGH', 'CRITICAL'].includes(patient.risk_level ?? '')).length;

  const acknowledge = async (alert: Alert) => {
    try {
      await predictionAPI.acknowledgeAlert(alert.alert_id);
      acknowledgeAlert(alert.alert_id);
      toast.success('Alert acknowledged');
    } catch {
      toast.error('Could not acknowledge this alert.');
    }
  };

  return (
    <main className="min-h-screen bg-[#f6f8fb] text-slate-900">
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-6 sm:px-6 lg:px-8">
          <div>
            <div className="flex items-center gap-3">
              <span className="rounded-xl bg-sky-600 p-2.5 text-white shadow-lg shadow-sky-200"><HeartPulse className="h-6 w-6" /></span>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-sky-600">CardioTwin / Clinical command center</p>
                <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl">Cardiac overview</h1>
              </div>
            </div>
            <p className="mt-3 text-sm text-slate-500">Live patient risk, vital signs, and predictive cardiac intelligence.</p>
          </div>
          <button
            type="button"
            onClick={() => void loadDashboardData(true)}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-sky-300 hover:text-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh telemetry
          </button>
        </div>
      </div>

      <div className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
        {error && (
          <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-800">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
            <div><p className="font-semibold">Dashboard unavailable</p><p className="mt-1 text-sm">{error}</p></div>
          </div>
        )}
        {dataWarning && !error && (
          <div className="flex items-center gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            <AlertTriangle className="h-5 w-5 shrink-0" />{dataWarning}
          </div>
        )}

        {isLoading ? (
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4"><LoadingCard /><LoadingCard /><LoadingCard /><LoadingCard /></div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Patients monitored" value={String(statistics?.total_patients ?? patients.length)} detail="Active cardiac care roster" icon={Activity} tone="bg-sky-50 text-sky-600" />
            <MetricCard label="Active alerts" value={String(statistics?.unacknowledged_alerts ?? activeAlerts)} detail={`${statistics?.critical_alerts ?? alerts.filter((alert) => alert.severity === 'CRITICAL').length} critical`} icon={ShieldAlert} tone="bg-red-50 text-red-600" />
            <MetricCard label="High-risk patients" value={String(highRiskCount)} detail="Requires clinical review" icon={AlertTriangle} tone="bg-orange-50 text-orange-600" />
            <MetricCard label="Average heart rate" value={averageHeartRate == null ? (statistics?.average_heart_rate == null ? '—' : `${Math.round(statistics.average_heart_rate)} bpm`) : `${averageHeartRate} bpm`} detail={averageOxygen ? `Mean SpO₂ ${averageOxygen}%` : 'No recent vitals'} icon={HeartPulse} tone="bg-emerald-50 text-emerald-600" />
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div><p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">Remote telemetry</p><h2 className="mt-1 text-xl font-bold text-slate-950">Heart rate & blood pressure</h2></div>
              <div className="flex gap-4 text-xs font-medium text-slate-500"><span className="flex items-center gap-1.5"><i className="h-2 w-2 rounded-full bg-sky-500" />Heart rate</span><span className="flex items-center gap-1.5"><i className="h-2 w-2 rounded-full bg-indigo-500" />Systolic BP</span></div>
            </div>
            <div className="mt-6 h-72">
              {trendData.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                    <defs><linearGradient id="heartRateFill" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.22} /><stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} /></linearGradient></defs>
                    <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" vertical={false} />
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                    <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0' }} />
                    <Area type="monotone" dataKey="heartRate" name="Heart rate (bpm)" stroke="#0ea5e9" strokeWidth={3} fill="url(#heartRateFill)" connectNulls />
                    <Area type="monotone" dataKey="systolic" name="Systolic BP (mmHg)" stroke="#6366f1" strokeWidth={2} fill="transparent" connectNulls />
                  </AreaChart>
                </ResponsiveContainer>
              ) : <EmptyState icon={Activity} title="No telemetry yet" message="Patient vital signs will appear here as wearable data arrives." />}
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">Risk stratification</p>
            <h2 className="mt-1 text-xl font-bold text-slate-950">Patient risk mix</h2>
            <div className="mt-4 h-52">
              {patients.length ? <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={riskDistribution} dataKey="value" nameKey="name" innerRadius={58} outerRadius={82} paddingAngle={4}>{riskDistribution.map((entry) => <Cell key={entry.name} fill={entry.color} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer> : <EmptyState icon={Activity} title="No patients" message="The risk mix will populate after the roster loads." />}
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">{riskDistribution.map((risk) => <div key={risk.name} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2"><span className="flex items-center gap-2 text-slate-600"><i className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: risk.color }} />{risk.name}</span><strong>{risk.value}</strong></div>)}</div>
          </section>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">Model output</p><h2 className="mt-1 text-xl font-bold text-slate-950">Prediction watchlist</h2></div><span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{predictionRows.length} scored</span></div>
            <div className="mt-5 overflow-x-auto">{predictionRows.length ? <table className="w-full min-w-[560px] text-left text-sm"><thead className="border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500"><tr><th className="pb-3 font-semibold">Patient</th><th className="pb-3 font-semibold">Event probability</th><th className="pb-3 font-semibold">Rhythm</th><th className="pb-3 font-semibold">BP trend</th></tr></thead><tbody className="divide-y divide-slate-100">{predictionRows.map(({ patient, prediction }) => <tr key={patient.patient_id}><td className="py-4"><p className="font-semibold text-slate-900">{patient.name}</p><p className="text-xs text-slate-500">{patient.patient_id}</p></td><td className="py-4"><div className="flex items-center gap-3"><div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100"><div className={`h-full rounded-full ${prediction!.cardiac_event_probability >= 0.7 ? 'bg-red-500' : prediction!.cardiac_event_probability >= 0.4 ? 'bg-amber-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(prediction!.cardiac_event_probability * 100, 100)}%` }} /></div><span className="font-semibold">{(prediction!.cardiac_event_probability * 100).toFixed(1)}%</span></div><span className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${riskBadge(prediction!.risk_classification)}`}>{prediction!.risk_classification}</span></td><td className="py-4 text-slate-600">{prediction!.arrhythmia_risk}</td><td className="py-4"><span className="inline-flex items-center gap-1 text-slate-600">{prediction!.blood_pressure_trend === 'RISING' ? <ArrowUpRight className="h-4 w-4 text-red-500" /> : prediction!.blood_pressure_trend === 'FALLING' ? <ArrowDownRight className="h-4 w-4 text-sky-500" /> : <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />}{prediction!.blood_pressure_trend}</span></td></tr>)}</tbody></table> : <EmptyState icon={HeartPulse} title="No predictions available" message="Predictions appear when patients are returned by the API." />}</div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">Needs attention</p><h2 className="mt-1 text-xl font-bold text-slate-950">Recent alerts</h2></div><span className="rounded-full bg-red-50 px-3 py-1 text-xs font-bold text-red-600">{activeAlerts} active</span></div>
            <div className="mt-5 space-y-3">{alerts.length ? alerts.slice(0, 5).map((alert) => <div key={alert.alert_id} className={`rounded-xl border p-4 ${alert.acknowledged ? 'border-slate-200 bg-slate-50' : alert.severity === 'CRITICAL' ? 'border-red-200 bg-red-50' : alert.severity === 'HIGH' ? 'border-orange-200 bg-orange-50' : 'border-amber-200 bg-amber-50'}`}><div className="flex items-start justify-between gap-3"><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ring-1 ${riskBadge(alert.severity)}`}>{alert.severity}</span><span className="text-xs text-slate-500">{alert.alert_type}</span></div><p className="mt-2 text-sm font-semibold text-slate-900">{alert.message}</p><p className="mt-1 text-xs text-slate-500">{patientNames[alert.patient_id] ?? alert.patient_id} · {formatDateTime(alert.timestamp)}</p></div>{!alert.acknowledged ? <button type="button" onClick={() => void acknowledge(alert)} className="shrink-0 rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white transition hover:bg-slate-700">Acknowledge</button> : <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600" />}</div></div>) : <EmptyState icon={CheckCircle2} title="All clear" message="No cardiac alerts have been reported." />}</div>
          </section>
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 text-xs text-slate-500 shadow-sm"><span className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald-500" />Connected to CardioTwin API</span><span className="flex items-center gap-2"><Wind className="h-4 w-4" />Auto-refresh every 30 seconds</span></div>
      </div>
    </main>
  );
}

function EmptyState({ icon: Icon, title, message }: { icon: typeof Activity; title: string; message: string }) {
  return <div className="flex h-full min-h-40 flex-col items-center justify-center text-center"><Icon className="h-8 w-8 text-slate-300" /><p className="mt-3 font-semibold text-slate-700">{title}</p><p className="mt-1 max-w-xs text-sm text-slate-500">{message}</p></div>;
}
