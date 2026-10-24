'use client';

import Link from 'next/link';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import toast from 'react-hot-toast';
import {
  Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { ArrowLeft, Download, HeartPulse, Moon, Printer, RefreshCw, Radio, Save, Trash2 } from 'lucide-react';
import {
  Alert, Baseline, CardiacPrediction, FamilyData, Patient, PatientInput, RiskExplanation,
  VitalSigns, familyAPI, patientAPI, patientSocketUrl, predictionAPI, sensorAPI, simulationAPI,
} from '@/lib/api';

const tabs = ['Overview', 'EHR', 'Vitals', 'What-if', 'Risk explanation', 'Alerts', 'Family'] as const;
type Tab = typeof tabs[number];
const disclaimer = 'Synthetic demo data. Not a medical device. Not for clinical decisions.';
const toInput = (patient: Patient): PatientInput => ({
  name: patient.name, age: patient.age, gender: patient.gender, email: patient.email, phone: patient.phone,
  bmi: patient.bmi, height_cm: patient.height_cm ?? null, weight_kg: patient.weight_kg ?? null,
  smoker: Boolean(patient.smoker), diabetes: Boolean(patient.diabetes), hypertension: Boolean(patient.hypertension),
  family_history_cvd: Boolean(patient.family_history_cvd), family_history_hypertension: Boolean(patient.family_history_hypertension),
  total_cholesterol: patient.total_cholesterol ?? 200, hdl_cholesterol: patient.hdl_cholesterol ?? 50,
  ldl_cholesterol: patient.ldl_cholesterol ?? 120, medications: patient.medications ?? [], medical_history: patient.medical_history ?? [],
});

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [vitals, setVitals] = useState<VitalSigns[]>([]);
  const [prediction, setPrediction] = useState<CardiacPrediction | null>(null);
  const [baseline, setBaseline] = useState<Baseline | null>(null);
  const [explanation, setExplanation] = useState<RiskExplanation | null>(null);
  const [family, setFamily] = useState<FamilyData | null>(null);
  const [summary, setSummary] = useState('');
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [tab, setTab] = useState<Tab>('Overview');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [live, setLive] = useState(false);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [range, setRange] = useState(24);
  const [showHR, setShowHR] = useState(true);
  const [showBP, setShowBP] = useState(true);
  const [showSpO2, setShowSpO2] = useState(true);
  const [patientDraft, setPatientDraft] = useState<PatientInput | null>(null);
  const [vitalDraft, setVitalDraft] = useState<VitalSigns>({ heart_rate_bpm: 72, blood_pressure_systolic: 120, blood_pressure_diastolic: 80, oxygen_saturation: 98, ecg_rhythm: 'Normal sinus rhythm', ecg_quality: 'GOOD', source: 'dashboard' });
  const [whatIfDraft, setWhatIfDraft] = useState({ heart_rate_bpm: 72, blood_pressure_systolic: 120, blood_pressure_diastolic: 80, oxygen_saturation: 98, smoker: false, diabetes: false });
  const [whatIfResult, setWhatIfResult] = useState<CardiacPrediction | null>(null);
  const [severity, setSeverity] = useState('ALL');
  const [showAcknowledged, setShowAcknowledged] = useState(false);
  const [contactDraft, setContactDraft] = useState({ name: '', phone: '' });
  const [selectedPoint, setSelectedPoint] = useState(0);
  const [replayRisk, setReplayRisk] = useState<CardiacPrediction | null>(null);
  const [dark, setDark] = useState(false);

  const refresh = useCallback(async (manual = false) => {
    if (manual) setRefreshing(true);
    else setLoading(true);
    setError('');
    try {
      const results = await Promise.all([
        patientAPI.getPatient(id), sensorAPI.getVitals(id, 100), predictionAPI.predictCardiac(id),
        sensorAPI.getBaseline(id), predictionAPI.explain(id), patientAPI.getSummary(id),
        predictionAPI.getAlerts(id), familyAPI.get(id),
      ]);
      setPatient(results[0].data); setPatientDraft(toInput(results[0].data));
      setVitals(results[1].data ?? []); setPrediction(results[2].data); setBaseline(results[3].data);
      setExplanation(results[4].data); setSummary(results[5].data.summary); setAlerts(results[6].data ?? []);
      setFamily(results[7].data); setContactDraft(results[7].data.contact ?? { name: '', phone: '' });
      const latest = results[1].data?.at(-1);
      if (latest) setWhatIfDraft((draft) => ({
        ...draft,
        heart_rate_bpm: latest.heart_rate_bpm ?? draft.heart_rate_bpm,
        blood_pressure_systolic: latest.blood_pressure_systolic ?? draft.blood_pressure_systolic,
        blood_pressure_diastolic: latest.blood_pressure_diastolic ?? draft.blood_pressure_diastolic,
        oxygen_saturation: latest.oxygen_saturation ?? draft.oxygen_saturation,
        smoker: Boolean(results[0].data.smoker), diabetes: Boolean(results[0].data.diabetes),
      }));
    } catch (loadError) {
      const message = loadError instanceof Error ? loadError.message : 'Unable to load this patient.';
      setError(message); toast.error(message);
    } finally { setLoading(false); setRefreshing(false); }
  }, [id]);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(true), 30000);
    const enabled = localStorage.getItem('cardiotwin-dark-mode') === 'true';
    setDark(enabled); document.documentElement.classList.toggle('dark', enabled);
    return () => { window.clearInterval(timer); socket?.close(); };
  // WebSocket lifecycle is controlled by live button; do not recreate it on every refresh.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refresh]);

  useEffect(() => {
    if (!vitals.length) return;
    const index = Math.max(0, Math.min(selectedPoint, vitals.length - 1));
    const point = vitals[index];
    const timer = window.setTimeout(async () => {
      try {
        const result = await predictionAPI.whatIf(id, point);
        setReplayRisk(result.data);
      } catch { setReplayRisk(null); }
    }, 300);
    return () => window.clearTimeout(timer);
  }, [id, selectedPoint, vitals]);

  const chartData = useMemo(() => vitals.slice(-range).map((v, index) => ({
    ...v, index, time: v.timestamp ? new Date(v.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : `#${index + 1}`,
  })), [vitals, range]);

  const toggleDark = () => {
    setDark((current) => { const next = !current; localStorage.setItem('cardiotwin-dark-mode', String(next)); document.documentElement.classList.toggle('dark', next); return next; });
  };

  const addVital = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const { heart_rate_bpm: hr, blood_pressure_systolic: sbp, blood_pressure_diastolic: dbp, oxygen_saturation: spo2 } = vitalDraft;
    if (hr == null || hr < 20 || hr > 250) return toast.error('Heart rate must be between 20 and 250 bpm.');
    if (sbp == null || sbp < 50 || sbp > 300) return toast.error('Systolic BP must be between 50 and 300 mmHg.');
    if (dbp == null || dbp < 30 || dbp > 200) return toast.error('Diastolic BP must be between 30 and 200 mmHg.');
    if (spo2 == null || spo2 < 50 || spo2 > 100) return toast.error('SpO2 must be between 50 and 100%.');
    try { await sensorAPI.submitVitals(id, vitalDraft); toast.success('Vital reading added'); await refresh(true); }
    catch (saveError) { toast.error(saveError instanceof Error ? saveError.message : 'Could not save vital reading.'); }
  };

  const saveEhr = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!patientDraft) return;
    try { await patientAPI.updatePatient(id, patientDraft); toast.success('EHR saved'); await refresh(true); }
    catch (saveError) { toast.error(saveError instanceof Error ? saveError.message : 'Could not save EHR.'); }
  };

  const removePatient = async () => {
    if (!window.confirm(`Delete ${patient?.name ?? 'this patient'} and all associated readings and alerts?`)) return;
    try { await patientAPI.deletePatient(id); toast.success('Patient deleted'); window.location.href = '/dashboard'; }
    catch { toast.error('Could not delete patient.'); }
  };

  const runWhatIf = async () => {
    try { const result = await predictionAPI.whatIf(id, whatIfDraft); setWhatIfResult(result.data); toast.success('What-if prediction ready'); }
    catch (runError) { toast.error(runError instanceof Error ? runError.message : 'What-if request failed.'); }
  };

  const saveFamily = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try { await familyAPI.save(id, contactDraft); toast.success('Family contact saved'); await refresh(true); }
    catch (saveError) { toast.error(saveError instanceof Error ? saveError.message : 'Could not save contact.'); }
  };

  const acknowledge = async (alert: Alert) => {
    try { const result = await predictionAPI.acknowledgeAlert(alert.alert_id); setAlerts((items) => items.map((item) => item.alert_id === alert.alert_id ? result.data : item)); toast.success('Alert acknowledged'); }
    catch { toast.error('Could not acknowledge alert.'); }
  };

  const startLive = async () => {
    try {
      await simulationAPI.start(id);
      const nextSocket = new WebSocket(patientSocketUrl(id));
      nextSocket.onopen = () => { nextSocket.send(JSON.stringify({ type: 'subscribe' })); setLive(true); };
      nextSocket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'vitals') setVitals((items) => [...items, message.data].slice(-100));
          if (message.type === 'alert') setAlerts((items) => [message.data, ...items]);
          if (message.type === 'prediction_update') setPrediction(message);
        } catch { /* Ignore malformed demo frames. */ }
      };
      nextSocket.onerror = () => toast.error('Live socket disconnected. Refresh to retry.');
      setSocket(nextSocket); toast.success('Live monitoring started');
    } catch { toast.error('Could not start live monitoring.'); }
  };

  const stopLive = async () => {
    try { await simulationAPI.stop(id); socket?.close(); setSocket(null); setLive(false); toast.success('Live monitoring stopped'); }
    catch { toast.error('Could not stop live monitoring.'); }
  };

  const downloadExport = async () => {
    try {
      const result = await patientAPI.exportPatient(id);
      const url = URL.createObjectURL(new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' }));
      const anchor = document.createElement('a'); anchor.href = url; anchor.download = `${id}-cardiotwin-export.json`; anchor.click(); URL.revokeObjectURL(url);
      toast.success('JSON export downloaded');
    } catch { toast.error('Export failed.'); }
  };

  if (loading) return <main className="min-h-screen bg-[#f6f8fb] p-8"><p className="animate-pulse text-slate-500">Loading patient twin…</p></main>;
  if (error && !patient) return <main className="min-h-screen bg-[#f6f8fb] p-8"><p className="text-red-700">{error}</p><button onClick={() => void refresh(true)} className="mt-4 rounded-xl bg-sky-600 px-4 py-2 text-white">Retry</button></main>;
  if (!patient) return null;

  const visibleAlerts = alerts.filter((item) => (severity === 'ALL' || item.severity === severity) && (showAcknowledged || !item.acknowledged));
  const activeRisk = prediction?.risk_classification ?? patient.risk_level ?? 'LOW';
  const streak = family?.flag_streak ?? 0;

  return <main className="min-h-screen bg-[#f6f8fb] text-slate-900">
    <header className="border-b border-slate-200 bg-white"><div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-5 sm:px-6">
      <div><Link href="/dashboard" className="inline-flex items-center gap-2 text-sm font-semibold text-sky-700"><ArrowLeft size={16} />Patient roster</Link><div className="mt-2 flex items-center gap-3"><span className="rounded-xl bg-sky-600 p-2 text-white"><HeartPulse size={21} /></span><div><h1 className="text-2xl font-bold">{patient.name}</h1><p className="text-sm text-slate-500">{patient.patient_id} · {patient.age} years · {patient.gender}</p></div></div></div>
      <div className="flex flex-wrap gap-2"><button onClick={() => void refresh(true)} disabled={refreshing} className="btn"><RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />Refresh</button><button onClick={toggleDark} className="btn"><Moon size={15} />{dark ? 'Light mode' : 'Dark mode'}</button><button onClick={downloadExport} className="btn"><Download size={15} />Export JSON</button><button onClick={() => window.print()} className="btn"><Printer size={15} />Print report</button><button onClick={removePatient} className="btn text-red-700"><Trash2 size={15} />Delete</button></div>
    </div></header>
    <div className="mx-auto max-w-7xl space-y-5 px-4 py-6 sm:px-6">
      <nav className="flex gap-2 overflow-x-auto rounded-2xl border border-slate-200 bg-white p-2">{tabs.map((item) => <button key={item} onClick={() => setTab(item)} className={`whitespace-nowrap rounded-xl px-4 py-2 text-sm font-semibold ${tab === item ? 'bg-sky-600 text-white' : 'text-slate-600 hover:bg-slate-100'}`}>{item}</button>)}</nav>
      {error && <p className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</p>}

      {tab === 'Overview' && <div className="space-y-5">
        <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
          <section className="card"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="eyebrow">Clinical summary</p><p className="mt-2 leading-7 text-slate-700">{summary || 'No summary available.'}</p></div><span className={`risk ${activeRisk}`}>{activeRisk}</span></div><p className="mt-4 text-xs text-slate-500">{disclaimer}</p></section>
          <section className="card"><p className="eyebrow">Live monitoring</p><div className="mt-3 flex items-center justify-between"><div><p className="text-xl font-bold">{live ? <span className="text-red-600"><i className="mr-2 inline-block h-2 w-2 animate-pulse rounded-full bg-red-500" />LIVE</span> : 'Stopped'}</p><p className="mt-1 text-sm text-slate-500">Synthetic wearable simulation · 3 seconds</p></div>{live ? <button onClick={() => void stopLive()} className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white">Stop</button> : <button onClick={() => void startLive()} className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white"><Radio size={15} />Start live monitoring</button>}</div><p className="mt-4 text-sm text-slate-600">Flag streak: <b>{streak} of 3 flagged</b></p></section>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[
          ['Heart rate', baseline?.latest?.heart_rate_bpm != null ? `${baseline.latest.heart_rate_bpm} bpm` : '—'],
          ['Blood pressure', baseline?.latest?.blood_pressure_systolic != null ? `${baseline.latest.blood_pressure_systolic}/${baseline.latest.blood_pressure_diastolic}` : '—'],
          ['SpO2', baseline?.latest?.oxygen_saturation != null ? `${baseline.latest.oxygen_saturation}%` : '—'],
          ['Event risk estimate', `${Math.round((prediction?.cardiac_event_probability ?? 0) * 100)}%`],
        ].map(([label, value]) => <div key={label} className="card"><p className="eyebrow">{label}</p><p className="mt-2 text-2xl font-bold">{value}</p></div>)}</div>
        <BaselineCard baseline={baseline} />
        <TrendChart data={chartData} range={range} setRange={setRange} showHR={showHR} setShowHR={setShowHR} showBP={showBP} setShowBP={setShowBP} showSpO2={showSpO2} setShowSpO2={setShowSpO2} />
        <section className="card"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="eyebrow">Digital twin timeline</p><h2 className="mt-1 text-lg font-bold">Replay a reading</h2></div><p className="text-sm text-slate-500">Historical replay estimate, without saving changes</p></div>{vitals.length ? <><input aria-label="Replay reading" type="range" min={0} max={vitals.length - 1} value={Math.min(selectedPoint, vitals.length - 1)} onChange={(e) => setSelectedPoint(Number(e.target.value))} className="mt-5 w-full" /><div className="mt-3 flex flex-wrap justify-between gap-3 text-sm"><span>{new Date(vitals[Math.min(selectedPoint, vitals.length - 1)].timestamp ?? Date.now()).toLocaleString()}</span><span>HR {vitals[Math.min(selectedPoint, vitals.length - 1)].heart_rate_bpm ?? '—'} · BP {vitals[Math.min(selectedPoint, vitals.length - 1)].blood_pressure_systolic ?? '—'}/{vitals[Math.min(selectedPoint, vitals.length - 1)].blood_pressure_diastolic ?? '—'} · SpO2 {vitals[Math.min(selectedPoint, vitals.length - 1)].oxygen_saturation ?? '—'}%</span><b>Estimated risk: {replayRisk?.risk_classification ?? 'Calculating…'}</b></div></> : <Empty text="Add readings to build the patient timeline." />}</section>
      </div>}

      {tab === 'EHR' && patientDraft && <form onSubmit={saveEhr} className="card"><div className="flex items-center justify-between"><div><p className="eyebrow">Electronic health record</p><h2 className="mt-1 text-lg font-bold">Patient details</h2></div><button className="inline-flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-2 text-sm font-semibold text-white"><Save size={15} />Save EHR</button></div><div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{(['name','age','gender','email','phone','bmi','height_cm','weight_kg','total_cholesterol','hdl_cholesterol','ldl_cholesterol'] as const).map((key) => <label key={key} className="field">{key.replaceAll('_', ' ')}<input required={['name','age','gender','email','phone','bmi'].includes(key)} type={['age','bmi','height_cm','weight_kg','total_cholesterol','hdl_cholesterol','ldl_cholesterol'].includes(key) ? 'number' : 'text'} step="any" value={patientDraft[key] ?? ''} onChange={(e) => setPatientDraft({ ...patientDraft, [key]: ['age','bmi','height_cm','weight_kg','total_cholesterol','hdl_cholesterol','ldl_cholesterol'].includes(key) ? Number(e.target.value) : e.target.value } as PatientInput)} /></label>)}{([['smoker','Smoker'],['diabetes','Diabetes'],['hypertension','Hypertension'],['family_history_cvd','Family history CVD'],['family_history_hypertension','Family history of hypertension']] as const).map(([key,label]) => <label key={key} className="flex items-center gap-2 rounded-xl border border-slate-200 p-3 text-sm"><input type="checkbox" checked={Boolean(patientDraft[key])} onChange={(e) => setPatientDraft({ ...patientDraft, [key]: e.target.checked })} />{label}</label>)}<label className="field">Medications (comma separated)<input value={patientDraft.medications?.join(', ') ?? ''} onChange={(e) => setPatientDraft({ ...patientDraft, medications: e.target.value.split(',').map((x) => x.trim()).filter(Boolean) })} /></label><label className="field">Medical history (comma separated)<input value={patientDraft.medical_history?.join(', ') ?? ''} onChange={(e) => setPatientDraft({ ...patientDraft, medical_history: e.target.value.split(',').map((x) => x.trim()).filter(Boolean) })} /></label></div></form>}

      {tab === 'Vitals' && <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]"><form onSubmit={addVital} className="card h-fit"><p className="eyebrow">Manual telemetry</p><h2 className="mt-1 text-lg font-bold">Add vital reading</h2><div className="mt-4 grid grid-cols-2 gap-3">{([['heart_rate_bpm','Heart rate',20,250],['blood_pressure_systolic','Systolic BP',50,300],['blood_pressure_diastolic','Diastolic BP',30,200],['oxygen_saturation','SpO2',50,100]] as const).map(([key,label,min,max]) => <label key={key} className="field">{label}<input type="number" required min={min} max={max} value={vitalDraft[key] ?? ''} onChange={(e) => setVitalDraft({ ...vitalDraft, [key]: Number(e.target.value) })} /></label>)}<label className="field">ECG rhythm<select value={vitalDraft.ecg_rhythm ?? ''} onChange={(e) => setVitalDraft({ ...vitalDraft, ecg_rhythm: e.target.value })}>{['Normal sinus rhythm','Tachycardia','Bradycardia','AFib','PVC','ST Elevation','T Wave Inversion'].map((x) => <option key={x}>{x}</option>)}</select></label><label className="field">ECG quality<select value={vitalDraft.ecg_quality ?? 'GOOD'} onChange={(e) => setVitalDraft({ ...vitalDraft, ecg_quality: e.target.value })}>{['GOOD','FAIR','POOR'].map((x) => <option key={x}>{x}</option>)}</select></label><label className="field col-span-2">Source<input value={vitalDraft.source ?? ''} onChange={(e) => setVitalDraft({ ...vitalDraft, source: e.target.value })} /></label></div><button className="mt-4 w-full rounded-xl bg-sky-600 px-4 py-2.5 font-semibold text-white">Save reading</button><p className="mt-2 text-xs text-slate-500">HR 20–250 · SBP 50–300 · DBP 30–200 · SpO2 50–100</p></form><div className="space-y-5"><TrendChart data={chartData} range={range} setRange={setRange} showHR={showHR} setShowHR={setShowHR} showBP={showBP} setShowBP={setShowBP} showSpO2={showSpO2} setShowSpO2={setShowSpO2} /><ReadingList vitals={vitals} /></div></div>}

      {tab === 'What-if' && <div className="grid gap-5 lg:grid-cols-2"><section className="card"><p className="eyebrow">Scenario builder</p><h2 className="mt-1 text-lg font-bold">Hypothetical values</h2><div className="mt-4 space-y-4">{([['heart_rate_bpm','Heart rate',20,250],['blood_pressure_systolic','Systolic BP',50,300],['blood_pressure_diastolic','Diastolic BP',30,200]] as const).map(([key,label,min,max]) => <label key={key} className="field">{label}: {whatIfDraft[key]}<input type="range" min={min} max={max} value={whatIfDraft[key]} onChange={(e) => setWhatIfDraft({ ...whatIfDraft, [key]: Number(e.target.value) })} /><input type="number" min={min} max={max} value={whatIfDraft[key]} onChange={(e) => setWhatIfDraft({ ...whatIfDraft, [key]: Number(e.target.value) })} /></label>)}<label className="field">SpO2<input type="number" min={50} max={100} value={whatIfDraft.oxygen_saturation} onChange={(e) => setWhatIfDraft({ ...whatIfDraft, oxygen_saturation: Number(e.target.value) })} /></label><label className="flex items-center gap-2"><input type="checkbox" checked={whatIfDraft.smoker} onChange={(e) => setWhatIfDraft({ ...whatIfDraft, smoker: e.target.checked })} />Smoking</label><label className="flex items-center gap-2"><input type="checkbox" checked={whatIfDraft.diabetes} onChange={(e) => setWhatIfDraft({ ...whatIfDraft, diabetes: e.target.checked })} />Diabetes</label><button onClick={() => void runWhatIf()} className="rounded-xl bg-sky-600 px-4 py-2.5 font-semibold text-white">Simulate</button></div><p className="mt-4 text-sm font-semibold text-amber-700">What-if only, history unchanged</p></section><section className="card"><p className="eyebrow">Side-by-side comparison</p><div className="mt-4 grid gap-4 sm:grid-cols-2"><RiskComparison label="Current risk" prediction={prediction} /><RiskComparison label="Simulated risk" prediction={whatIfResult} /></div>{whatIfResult && <p className="mt-4 text-sm text-slate-600">Estimated event probability: {Math.round((prediction?.cardiac_event_probability ?? 0) * 100)}% → {Math.round(whatIfResult.cardiac_event_probability * 100)}%</p>}</section></div>}

      {tab === 'Risk explanation' && <section className="card"><p className="eyebrow">Deterministic score breakdown</p><h2 className="mt-1 text-lg font-bold">Contributing factors</h2>{explanation ? <><div className="mt-5 space-y-3">{explanation.factors.map((factor) => <div key={factor.factor} className="grid grid-cols-[140px_1fr_46px] items-center gap-3 text-sm"><span>{factor.factor}</span><div className="h-3 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-sky-600" style={{ width: `${Math.max(factor.points / explanation.divisor * 100, factor.points ? 5 : 0)}%` }} /></div><b className="text-right">+{factor.points}</b></div>)}</div><div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-4"><p>Total: <b>{explanation.total_points} / {explanation.divisor}</b></p><p>Risk probability: <b>{Math.round(explanation.probability * 100)}%</b></p><span className={`risk ${explanation.final_class}`}>{explanation.final_class}</span></div><p className="mt-3 text-xs text-slate-500">Uses the same simplified Framingham point rules as the active scorer. This is synthetic demo output.</p></> : <Empty text="Risk explanation is unavailable." />}</section>}

      {tab === 'Alerts' && <section className="card"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="eyebrow">Alert queue</p><h2 className="mt-1 text-lg font-bold">{alerts.filter((a) => !a.acknowledged).length} active alerts</h2><p className="mt-1 text-sm text-slate-500">{streak} of 3 flagged summaries</p></div><label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={showAcknowledged} onChange={(e) => setShowAcknowledged(e.target.checked)} />Show acknowledged</label></div><div className="mt-4 flex gap-2">{['ALL','CRITICAL','HIGH','MEDIUM'].map((level) => <button key={level} onClick={() => setSeverity(level)} className={`rounded-full px-3 py-1.5 text-xs font-bold ${severity === level ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600'}`}>{level}</button>)}</div><div className="mt-4 space-y-3">{visibleAlerts.map((alert) => <div key={alert.alert_id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-4"><div><span className={`risk ${alert.severity}`}>{alert.severity}</span><p className="mt-2 font-semibold">{alert.message}</p><p className="mt-1 text-xs text-slate-500">{new Date(alert.timestamp).toLocaleString()}</p></div>{alert.acknowledged ? <span className="text-sm text-emerald-700">Acknowledged</span> : <button onClick={() => void acknowledge(alert)} className="rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white">Acknowledge</button>}</div>)}{!visibleAlerts.length && <Empty text="No alerts match this filter." />}</div></section>}

      {tab === 'Family' && <div className="grid gap-5 lg:grid-cols-2"><form onSubmit={saveFamily} className="card h-fit"><p className="eyebrow">Family contact</p><h2 className="mt-1 text-lg font-bold">Contact details</h2><div className="mt-4 grid gap-3"><label className="field">Name<input required value={contactDraft.name} onChange={(e) => setContactDraft({ ...contactDraft, name: e.target.value })} /></label><label className="field">Phone<input required value={contactDraft.phone} onChange={(e) => setContactDraft({ ...contactDraft, phone: e.target.value })} /></label></div><button className="mt-4 inline-flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-2 text-sm font-semibold text-white"><Save size={15} />Save contact</button></form><section className="card"><p className="eyebrow">Simulated notification log</p><h2 className="mt-1 text-lg font-bold">Family alerts</h2><div className="mt-4 space-y-3">{family?.notifications.map((notification) => <article key={notification.notification_id} className="rounded-xl border border-slate-200 p-4"><div className="flex justify-between gap-2"><b>{notification.status.replaceAll('_', ' ')}</b><span className="text-xs text-slate-500">{new Date(notification.timestamp).toLocaleString()}</span></div><p className="mt-2 text-sm">{notification.message}</p><p className="mt-2 text-xs font-semibold uppercase text-sky-700">Simulated</p></article>)}{!family?.notifications.length && <Empty text="No simulated family notifications yet." />}</div></section></div>}

      <section className="print-only"><h1>CardioTwin Patient Report</h1><p>{patient.name} · {patient.patient_id} · {patient.age} years · {patient.gender}</p><p>Generated {new Date().toLocaleString()}</p><h2>Clinical summary</h2><p>{summary}</p><h2>Current EHR</h2><p>BMI {patient.bmi} · Smoking {patient.smoker ? 'yes' : 'no'} · Diabetes {patient.diabetes ? 'yes' : 'no'} · Hypertension {patient.hypertension ? 'yes' : 'no'}</p><p>Cholesterol: total {patient.total_cholesterol ?? '—'}, HDL {patient.hdl_cholesterol ?? '—'}, LDL {patient.ldl_cholesterol ?? '—'}</p><p>Medications: {patient.medications?.join(', ') || 'None listed'}</p><h2>Latest vitals</h2><p>HR {baseline?.latest?.heart_rate_bpm ?? '—'} bpm · BP {baseline?.latest?.blood_pressure_systolic ?? '—'}/{baseline?.latest?.blood_pressure_diastolic ?? '—'} mmHg · SpO2 {baseline?.latest?.oxygen_saturation ?? '—'}%</p><p>Risk class {activeRisk} · Estimated event probability {Math.round((prediction?.cardiac_event_probability ?? 0) * 100)}%</p><h2>Risk factors</h2><p>{explanation?.factors.map((factor) => `${factor.factor} +${factor.points}`).join(' · ') || 'Unavailable'} · Total {explanation?.total_points ?? '—'} / 45</p><h2>Recent alerts</h2>{alerts.slice(0, 8).map((alert) => <p key={alert.alert_id}>{alert.severity} · {alert.message} · {new Date(alert.timestamp).toLocaleString()}</p>)}<p>Family contact: {family?.contact?.name || 'Not set'} {family?.contact?.phone || ''}</p><p>{disclaimer}</p></section>

      <footer className="rounded-2xl border border-slate-200 bg-white p-4 text-center text-xs text-slate-500">{disclaimer}</footer>
    </div>
  </main>;
}

function BaselineCard({ baseline }: { baseline: Baseline | null }) {
  if (!baseline) return <section className="card"><Empty text="Baseline unavailable." /></section>;
  const rows = [
    ['Heart rate', 'average_heart_rate_bpm', 'heart_rate_bpm', 'bpm'],
    ['Systolic BP', 'average_systolic_bp', 'blood_pressure_systolic', 'mmHg'],
    ['Diastolic BP', 'average_diastolic_bp', 'blood_pressure_diastolic', 'mmHg'],
    ['SpO2', 'average_oxygen_saturation', 'oxygen_saturation', '%'],
  ] as const;
  return <section className="card"><div className="flex flex-wrap items-center justify-between gap-2"><div><p className="eyebrow">Baseline comparison</p><h2 className="mt-1 text-lg font-bold">Patient average vs latest</h2></div>{baseline.large_deviation && <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">Large deviation</span>}</div><div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{rows.map(([label, averageKey, latestKey, unit]) => <div key={label} className="rounded-xl bg-slate-50 p-3"><p className="text-xs text-slate-500">{label}</p><p className="mt-1 font-bold">{baseline.average[averageKey] ?? '—'} {unit}</p><p className="mt-1 text-sm">Latest {baseline.latest?.[latestKey] ?? '—'} {unit}</p><p className={`mt-1 text-xs font-bold ${Math.abs(baseline.deviation_percent[latestKey] ?? 0) >= 20 ? 'text-amber-700' : 'text-slate-500'}`}>{baseline.deviation_percent[latestKey] == null ? 'No deviation' : `${baseline.deviation_percent[latestKey]! > 0 ? '+' : ''}${baseline.deviation_percent[latestKey]}% from average`}</p></div>)}</div></section>;
}

function TrendChart({ data, range, setRange, showHR, setShowHR, showBP, setShowBP, showSpO2, setShowSpO2 }: {
  data: Array<VitalSigns & { time: string; index: number }>;
  range: number; setRange: (value: number) => void;
  showHR: boolean; setShowHR: (value: boolean) => void; showBP: boolean; setShowBP: (value: boolean) => void;
  showSpO2: boolean; setShowSpO2: (value: boolean) => void;
}) {
  return <section className="card"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="eyebrow">Vital trends</p><h2 className="mt-1 text-lg font-bold">HR, BP and SpO2</h2></div><select aria-label="Trend time range" value={range} onChange={(e) => setRange(Number(e.target.value))} className="rounded-lg border border-slate-200 px-3 py-2 text-sm">{[12,24,50].map((n) => <option key={n} value={n}>Last {n} readings</option>)}</select></div><div className="mt-3 flex flex-wrap gap-3 text-xs"><Legend label="Heart rate" color="#0ea5e9" active={showHR} onClick={() => setShowHR(!showHR)} /><Legend label="Systolic BP" color="#6366f1" active={showBP} onClick={() => setShowBP(!showBP)} /><Legend label="SpO2" color="#10b981" active={showSpO2} onClick={() => setShowSpO2(!showSpO2)} /></div><div className="mt-3 h-64">{data.length ? <ResponsiveContainer width="100%" height="100%"><AreaChart data={data}><CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" vertical={false} /><XAxis dataKey="time" tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 10 }} /><Tooltip /><ReferenceLine y={120} stroke="#ef4444" strokeDasharray="5 4" /><ReferenceLine y={180} stroke="#f97316" strokeDasharray="5 4" /><ReferenceLine y={90} stroke="#10b981" strokeDasharray="5 4" />{showHR && <Area type="monotone" dataKey="heart_rate_bpm" name="HR bpm" stroke="#0ea5e9" fill="#0ea5e922" connectNulls />}{showBP && <Area type="monotone" dataKey="blood_pressure_systolic" name="Systolic mmHg" stroke="#6366f1" fill="transparent" connectNulls />}{showSpO2 && <Area type="monotone" dataKey="oxygen_saturation" name="SpO2 %" stroke="#10b981" fill="transparent" connectNulls />}</AreaChart></ResponsiveContainer> : <Empty text="No telemetry readings yet." />}</div></section>;
}

function Legend({ label, color, active, onClick }: { label: string; color: string; active: boolean; onClick: () => void }) { return <button type="button" onClick={onClick} className={`inline-flex items-center gap-2 rounded-full px-2 py-1 ${active ? 'bg-slate-100' : 'opacity-40'}`}><i className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />{label}</button>; }
function ReadingList({ vitals }: { vitals: VitalSigns[] }) { return <section className="card"><p className="eyebrow">Reading history</p><div className="mt-3 max-h-[520px] overflow-y-auto">{vitals.slice().reverse().map((v, index) => <div key={`${v.timestamp}-${index}`} className="flex flex-wrap justify-between gap-2 border-b border-slate-100 py-3 text-sm"><span>{v.timestamp ? new Date(v.timestamp).toLocaleString() : 'Unknown time'}</span><b>HR {v.heart_rate_bpm ?? '—'} · BP {v.blood_pressure_systolic ?? '—'}/{v.blood_pressure_diastolic ?? '—'} · SpO2 {v.oxygen_saturation ?? '—'}%</b></div>)}{!vitals.length && <Empty text="No readings recorded." />}</div></section>; }
function RiskComparison({ label, prediction }: { label: string; prediction: CardiacPrediction | null }) { return <div className="rounded-2xl bg-slate-50 p-5"><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-3xl font-bold">{prediction ? `${Math.round(prediction.cardiac_event_probability * 100)}%` : '—'}</p><p className="mt-2 text-sm">{prediction?.risk_classification ?? 'Run a simulation'}</p></div>; }
function Empty({ text }: { text: string }) { return <p className="py-8 text-center text-sm text-slate-500">{text}</p>; }
