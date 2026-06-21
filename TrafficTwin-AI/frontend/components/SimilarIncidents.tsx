'use client';

import React from 'react';
import { FileText, Clock } from 'lucide-react';

interface SimilarIncident {
  incident_id: number;
  similarity_score: number;
  summary: string;
}

interface SimilarIncidentsProps {
  incidents: SimilarIncident[];
  loading?: boolean;
}

export default function SimilarIncidents({ incidents, loading }: SimilarIncidentsProps) {
  return (
    <div className="card p-6">
      <div className="flex items-center gap-2 mb-4">
        <FileText size={20} className="text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-800">Similar Historical Cases</h3>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse h-20 bg-gray-100 rounded" />
          ))}
        </div>
      ) : incidents.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No similar cases found</p>
      ) : (
        <div className="space-y-3">
          {incidents.map((incident) => (
            <div
              key={incident.incident_id}
              className="p-3 bg-gray-50 rounded-md border border-gray-200 hover:bg-gray-100 transition"
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium text-gray-800">Case #{incident.incident_id}</h4>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                  {(incident.similarity_score * 100).toFixed(1)}% Similar
                </span>
              </div>
              <p className="text-sm text-gray-600">{incident.summary}</p>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 p-3 bg-blue-50 rounded-md text-sm text-blue-800">
        <p className="font-medium mb-1">💡 Insights from history:</p>
        <p>
          Review these similar cases to understand how previous incidents were resolved and what
          actions worked best.
        </p>
      </div>
    </div>
  );
}
