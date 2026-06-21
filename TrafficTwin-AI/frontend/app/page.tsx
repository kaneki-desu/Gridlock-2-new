'use client';

import React, { useState, useEffect } from 'react';
import IncidentForm from '@/components/IncidentForm';
import ResultCards from '@/components/ResultCards';
import SimilarIncidents from '@/components/SimilarIncidents';
import IncidentChart from '@/components/IncidentChart';
import IncidentMap from '@/components/IncidentMap';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { retrieveSimilar, updateIncidentStatus, IncidentInput } from '@/lib/api';
import { formatDate } from '@/lib/utils';

interface IncidentResult {
  incident_id: number;
  severity: string;
  predicted_clearance: number;
  diversion_required: boolean;
  urgency_level: string;
  similar_cases_found: number;
  llm_suggestions?: string;
}

interface SimilarCase {
  incident_id: number;
  similarity_score: number;
  summary: string;
}

interface CurrentIncident {
  localId: string;
  incident_id?: number;
  event_type: string;
  event_cause: string;
  priority: string;
  corridor?: string;
  zone?: string;
  junction?: string;
  address?: string;
  description?: string;
  start_datetime?: string;
  status: 'Open' | 'Resolved' | 'Closed';
  created_at: string;
  savedToDatabase: boolean;
}

export default function Dashboard() {
  const [result, setResult] = useState<IncidentResult | null>(null);
  const [similarCases, setSimilarCases] = useState<SimilarCase[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [success, setSuccess] = useState(false);
  const [currentIncidents, setCurrentIncidents] = useState<CurrentIncident[]>([]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const saved = window.localStorage.getItem('trafficTwinCurrentIncidents');
    if (saved) {
      try {
        setCurrentIncidents(JSON.parse(saved));
      } catch {
        setCurrentIncidents([]);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem('trafficTwinCurrentIncidents', JSON.stringify(currentIncidents));
  }, [currentIncidents]);

  const handleIncidentSubmitted = async (incidentData: IncidentInput, incident: IncidentResult) => {
    setResult(incident);
    setSuccess(true);

    const nextIncident: CurrentIncident = {
      localId: `${Date.now()}`,
      incident_id: incident.incident_id,
      event_type: incidentData.event_type,
      event_cause: incidentData.event_cause,
      priority: incidentData.priority,
      corridor: incidentData.corridor,
      zone: incidentData.zone,
      junction: incidentData.junction,
      address: incidentData.address,
      description: incidentData.description,
      start_datetime: incidentData.start_datetime,
      status: 'Open',
      created_at: incidentData.start_datetime || new Date().toISOString(),
      savedToDatabase: true,
    };

    setCurrentIncidents((prev) => [nextIncident, ...prev]);

    setLoadingSimilar(true);
    try {
      const retrieved = await retrieveSimilar(incidentData);
      setSimilarCases(retrieved.slice(0, 5));
    } catch (error) {
      console.error('Failed to load similar incidents', error);
      setSimilarCases([]);
    } finally {
      setLoadingSimilar(false);
    }

    // Hide success message after 5 seconds
    setTimeout(() => setSuccess(false), 5000);
  };

  const changeIncidentStatus = async (localId: string, nextStatus: 'Resolved' | 'Closed', incidentId?: number) => {
    const shouldPersist = window.confirm(`Mark incident as ${nextStatus}. Save this status update to the database?`);

    setCurrentIncidents((prev) =>
      prev.map((incident) =>
        incident.localId === localId
          ? { ...incident, status: nextStatus }
          : incident
      )
    );

    if (shouldPersist && incidentId) {
      try {
        await updateIncidentStatus(incidentId, nextStatus.toLowerCase());
      } catch (error) {
        console.error('Failed to persist status update', error);
      }
    }
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

              {result.llm_suggestions && (
                <div className="card p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">AI Suggestions</h3>
                  <p className="text-sm text-gray-700 whitespace-pre-line">{result.llm_suggestions}</p>
                </div>
              )}

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

      {/* Current Incident Board */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Current Incident Board</h2>
            <p className="text-gray-600">Track open incidents and mark status transitions.</p>
          </div>
        </div>

        {currentIncidents.length === 0 ? (
          <div className="p-6 text-center text-gray-500">No current incidents yet. Submit an incident to add one.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-xs font-medium text-gray-700 uppercase">ID</th>
                  <th className="px-4 py-3 text-xs font-medium text-gray-700 uppercase">Status</th>
                  <th className="px-4 py-3 text-xs font-medium text-gray-700 uppercase">Start Time</th>
                  <th className="px-4 py-3 text-xs font-medium text-gray-700 uppercase">Description</th>
                  <th className="px-4 py-3 text-xs font-medium text-gray-700 uppercase">Saved</th>
                  <th className="px-4 py-3 text-xs font-medium text-gray-700 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {currentIncidents.map((incident) => (
                  <tr key={incident.localId} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {incident.incident_id ? `#${incident.incident_id}` : incident.localId}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          incident.status === 'Open'
                            ? 'bg-blue-100 text-blue-800'
                            : incident.status === 'Resolved'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {incident.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {incident.start_datetime ? formatDate(incident.start_datetime) : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 max-w-xl break-words">
                      {incident.description || 'No description'}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${incident.savedToDatabase ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'}`}>
                        {incident.savedToDatabase ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm space-x-2">
                      {incident.status === 'Open' && (
                        <>
                          <button
                            onClick={() => changeIncidentStatus(incident.localId, 'Resolved', incident.incident_id)}
                            className="btn-secondary"
                          >
                            Mark Resolved
                          </button>
                          <button
                            onClick={() => changeIncidentStatus(incident.localId, 'Closed', incident.incident_id)}
                            className="btn-primary"
                          >
                            Mark Closed
                          </button>
                        </>
                      )}
                      {incident.status === 'Resolved' && (
                        <button
                          onClick={() => changeIncidentStatus(incident.localId, 'Closed', incident.incident_id)}
                          className="btn-primary"
                        >
                          Mark Closed
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
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
