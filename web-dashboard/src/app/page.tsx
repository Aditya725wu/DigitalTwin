'use client';

import React from 'react';
import Link from 'next/link';
import { BarChart3, Users, AlertCircle, TrendingUp } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-600 to-blue-800">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-blue-600">CardioTwin</h1>
            <div className="flex gap-4">
              <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 font-medium">
                Dashboard
              </Link>
              <Link href="/patients" className="text-gray-700 hover:text-blue-600 font-medium">
                Patients
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center text-white mb-16">
          <h2 className="text-5xl font-bold mb-4">CardioTwin</h2>
          <p className="text-xl text-blue-100 mb-8">
            AI-Powered Digital Twin for Proactive Cardiovascular Disease Management
          </p>
          <p className="text-lg text-blue-100 max-w-2xl mx-auto mb-8">
            Real-time cardiac monitoring, predictive alerts, and personalized interventions powered by advanced machine learning
          </p>
          <Link
            href="/dashboard"
            className="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition"
          >
            Go to Dashboard
          </Link>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <TrendingUp className="h-12 w-12 text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Predictive Analytics</h3>
            <p className="text-gray-600">Predict cardiac events 24-48 hours in advance</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Alerts</h3>
            <p className="text-gray-600">Real-time arrhythmia and hypertension alerts</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 text-center">
            <Users className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Multi-Patient Management</h3>
            <p className="text-gray-600">Monitor cardiac patients remotely</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 text-center">
            <BarChart3 className="h-12 w-12 text-purple-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Rich Analytics</h3>
            <p className="text-gray-600">ECG, heart rate, and BP trend analysis</p>
          </div>
        </div>
      </div>

      {/* Benefits */}
      <div className="bg-white py-16 mt-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">Why CardioTwin?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">For Patients</h3>
              <ul className="space-y-3 text-gray-700">
                <li>✓ Real-time heart rate & ECG monitoring</li>
                <li>✓ Early warning for cardiac events</li>
                <li>✓ Blood pressure trend analysis</li>
                <li>✓ Arrhythmia detection</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">For Cardiologists</h3>
              <ul className="space-y-3 text-gray-700">
                <li>✓ Remote cardiac monitoring</li>
                <li>✓ Risk stratification</li>
                <li>✓ Predictive intervention</li>
                <li>✓ Better cardiovascular outcomes</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
