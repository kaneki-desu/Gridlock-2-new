'use client';

import React from 'react';
import { AlertTriangle, TrendingUp, Zap } from 'lucide-react';
import { getSeverityColor, getUrgencyColor, formatTime } from '@/lib/utils';

interface ResultCardsProps {
  severity: string;
  predictedClearance: number;
  diversionRequired: boolean;
  urgencyLevel: string;
  similarCasesFound: number;
}

export default function ResultCards({
  severity,
  predictedClearance,
  diversionRequired,
  urgencyLevel,
  similarCasesFound,
}: ResultCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Severity Card */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">Severity Level</h3>
          <AlertTriangle size={20} className="text-yellow-600" />
        </div>
        <div className={`text-2xl font-bold ${getSeverityColor(severity)}`}>
          {severity}
        </div>
        <p className="text-xs text-gray-500 mt-2">Based on incident attributes</p>
      </div>

      {/* Clearance Time Card */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">Predicted Clearance</h3>
          <TrendingUp size={20} className="text-blue-600" />
        </div>
        <div className="text-2xl font-bold text-blue-600">{formatTime(predictedClearance)}</div>
        <p className="text-xs text-gray-500 mt-2">ML Prediction</p>
      </div>

      {/* Urgency Card */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">Urgency Level</h3>
          <Zap size={20} className="text-orange-600" />
        </div>
        <div className={`text-2xl font-bold ${getUrgencyColor(urgencyLevel)}`}>
          {urgencyLevel}
        </div>
        <p className="text-xs text-gray-500 mt-2">Recommended response</p>
      </div>

      {/* Similar Cases Card */}
      <div className="card p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">Similar Cases</h3>
          <span className="text-2xl font-bold">{similarCasesFound}</span>
        </div>
        <p className="text-xs text-gray-500">From historical data</p>
      </div>

      {/* Diversion Recommended */}
      <div className="card p-4 md:col-span-2 lg:col-span-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-600">Diversion Required</h3>
          <div
            className={`px-4 py-2 rounded-full font-medium ${
              diversionRequired
                ? 'bg-red-100 text-red-800'
                : 'bg-green-100 text-green-800'
            }`}
          >
            {diversionRequired ? 'YES - Divert Traffic' : 'NO - Direct Traffic OK'}
          </div>
        </div>
      </div>
    </div>
  );
}
