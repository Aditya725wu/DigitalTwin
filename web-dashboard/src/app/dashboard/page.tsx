'use client';

import React, { useEffect, useState } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { AlertCircle, TrendingUp, Heart, Activity, AlertTriangle } from 'lucide-react';
import { useDashboardStore } from '@/store/dashboard';
import { predictionAPI, patientAPI, analyticsAPI } from '@/lib/api';
import toast from 'react-hot-toast';

const COLORS = ['#0066cc', '#00c9a7', '#ffa502', '#ff4757'];

export default function Dashboard() {
  const [glucoseData, setGlucoseData] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const { patients, alerts, isLoading, setPatients, setAlerts, setIsLoading } = useDashboardStore();

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [patientsRes, statsRes] = await Promise.all([
        patientAPI.listPatients(),
        analyticsAPI.getStatistics(),
      ]);

      setPatients(patientsRes.data);
      setStats(statsRes.data);

      // Generate mock glucose data
      const mockGlucoseData = Array.from({ length: 24 }, (_, i) => ({
        time: `${i}:00`,
        glucose: Math.floor(100 + Math.sin(i / 4) * 30 + Math.random() * 20),
        target: 120,
      }));
      setGlucoseData(mockGlucoseData);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const riskDistribution = [
    { name: 'Low Risk', value: Math.floor(patients.length * 0.4) },
    { name: 'Medium Risk', value: Math.floor(patients.length * 0.35) },
    { name: 'High Risk', value: Math.floor(patients.length * 0.20) },
    { name: 'Critical', value: Math.floor(patients.length * 0.05) },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">DiabetesTwin Dashboard</h1>
          <p className="text-gray-600">Real-time patient monitoring and predictive analytics</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Total Patients</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{patients.length}</p>
              </div>
              <Activity className="h-12 w-12 text-blue-500 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Active Alerts</p>
                <p className="text-3xl font-bold text-red-600 mt-2">
                  {alerts.filter((a) => !a.acknowledged).length}
                </p>
              </div>
              <AlertCircle className="h-12 w-12 text-red-500 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">High Risk Patients</p>
                <p className="text-3xl font-bold text-orange-600 mt-2">
                  {stats?.high_risk_alerts || 0}
                </p>
              </div>
              <AlertTriangle className="h-12 w-12 text-orange-500 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Avg Glucose Level</p>
                <p className="text-3xl font-bold text-green-600 mt-2">145</p>
              </div>
              <Heart className="h-12 w-12 text-green-500 opacity-20" />
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Glucose Trend */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Glucose Trends (24h Average)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={glucoseData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="glucose" stroke="#0066cc" name="Glucose" />
                <Line type="monotone" dataKey="target" stroke="#00c9a7" name="Target" strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Risk Distribution */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Patient Risk Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Alerts</h2>
          <div className="space-y-4">
            {alerts.slice(0, 5).map((alert) => (
              <div
                key={alert.alert_id}
                className={`p-4 rounded-lg border-l-4 ${
                  alert.severity === 'CRITICAL'
                    ? 'border-red-500 bg-red-50'
                    : alert.severity === 'HIGH'
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-yellow-500 bg-yellow-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{alert.message}</p>
                    <p className="text-sm text-gray-600 mt-1">{alert.patient_id}</p>
                  </div>
                  {!alert.acknowledged && (
                    <button
                      onClick={() => predictionAPI.acknowledgeAlert(alert.alert_id)}
                      className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                    >
                      Acknowledge
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
