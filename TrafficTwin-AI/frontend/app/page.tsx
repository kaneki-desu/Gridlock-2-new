'use client';

import React, { useState, useEffect } from 'react';
import IncidentForm from '@/components/IncidentForm';
import ResultCards from '@/components/ResultCards';
import SimilarIncidents from '@/components/SimilarIncidents';
import IncidentChart from '@/components/IncidentChart';
import IncidentMap from '@/components/IncidentMap';
import { AlertCircle, CheckCircle } from 'lucide-react';

interface IncidentResult {
  incident_id: number;
  severity: string;
  predicted_clearance: number;
  diversion_required: boolean;
  urgency_level: string;
  similar_cases_found: number;
}

interface SimilarCase {
  incident_id: number;
  similarity_score: number;
  summary: string;
}

export default function Dashboard() {
  const [result, setResult] = useState<IncidentResult | null>(null);
  const [similarCases, setSimilarCases] = useState<SimilarCase[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleIncidentSubmitted = (incident: IncidentResult) => {
    setResult(incident);
    setSuccess(true);

    // Fetch similar cases
    setLoadingSimilar(true);
    // In a real scenario, this would call the API
    setSimilarCases([
      {
        incident_id: 101,
        similarity_score: 0.92,
        summary: 'Vehicle breakdown on Tumkur Road during peak hour, resolved in 38 minutes',
      },
      {
        incident_id: 102,
        similarity_score: 0.87,
        summary: 'LCV breakdown on Tumkur Road, heavy traffic congestion, resolved in 45 minutes',
      },
      {
        incident_id: 103,
        similarity_score: 0.81,
        summary: 'Heavy vehicle mechanical failure, diversion implemented, resolved in 52 minutes',
      },
    ]);
    setLoadingSimilar(false);

    // Hide success message after 5 seconds
    setTimeout(() => setSuccess(false), 5000);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Traffic Incident Dashboard</h1>
        <p className="text-gray-600">
          Report incidents, get AI-powered predictions, and access historical insights
        </p>
      </div>

      {/* Success Message */}
      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
          <CheckCircle className="text-green-600" size={24} />
          <div>
            <h3 className="font-bold text-green-800">Incident Reported Successfully</h3>
            <p className="text-green-700 text-sm">
              Incident #{result?.incident_id} has been created and analyzed
            </p>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Form */}
        <div className="lg:col-span-1">
          <IncidentForm onIncidentSubmitted={handleIncidentSubmitted} />
        </div>

        {/* Right Column - Results */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <>
              <ResultCards
                severity={result.severity}
                predictedClearance={result.predicted_clearance}
                diversionRequired={result.diversion_required}
                urgencyLevel={result.urgency_level}
                similarCasesFound={result.similar_cases_found}
              />

              <SimilarIncidents incidents={similarCases} loading={loadingSimilar} />
            </>
          ) : (
            <div className="card p-8 text-center">
              <AlertCircle className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-500 text-lg">
                Submit an incident to see predictions and recommendations
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Analytics Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Analytics & Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <IncidentChart
            data={[
              { name: 'Vehicle Breakdown', value: 145 },
              { name: 'Accidents', value: 89 },
              { name: 'Tree Fall', value: 34 },
              { name: 'Water Logging', value: 23 },
              { name: 'Congestion', value: 67 },
            ]}
            title="Incident Frequency by Type"
            dataKey="value"
            color="#0284c7"
          />

          <IncidentChart
            data={[
              { name: 'Tumkur Road', value: 42 },
              { name: 'ORR North', value: 35 },
              { name: 'Bellary Road', value: 28 },
              { name: 'Bannerghata', value: 31 },
              { name: 'Others', value: 52 },
            ]}
            title="Incidents by Corridor"
            dataKey="value"
            color="#f59e0b"
          />

          <IncidentChart
            data={[
              { name: 'Low', value: 89 },
              { name: 'Medium', value: 124 },
              { name: 'High', value: 76 },
            ]}
            title="Severity Distribution"
            dataKey="value"
            color="#ef4444"
          />

          <IncidentChart
            data={[
              { name: '0-15 min', value: 124 },
              { name: '15-30 min', value: 89 },
              { name: '30-60 min', value: 56 },
              { name: '60+ min', value: 20 },
            ]}
            title="Clearance Time Distribution"
            dataKey="value"
            color="#10b981"
          />
        </div>
      </div>

      {/* Map Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Incident Locations</h2>
        <IncidentMap
          incidents={[
            {
              id: 1,
              latitude: 13.0400041,
              longitude: 77.5180991,
              severity: 'High',
              eventCause: 'vehicle_breakdown',
            },
            {
              id: 2,
              latitude: 13.0827,
              longitude: 77.5979,
              severity: 'Medium',
              eventCause: 'tree_fall',
            },
            {
              id: 3,
              latitude: 12.9717,
              longitude: 77.6412,
              severity: 'Low',
              eventCause: 'pot_holes',
            },
          ]}
        />
      </div>
    </div>
  );
}
