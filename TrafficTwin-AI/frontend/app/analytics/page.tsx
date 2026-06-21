'use client';

import React from 'react';
import IncidentChart from '@/components/IncidentChart';

export default function AnalyticsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Analytics</h1>
        <p className="text-gray-600 mt-1">Traffic incident insights and trends</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-6">
          <p className="text-gray-600 text-sm mb-2">Total Incidents</p>
          <p className="text-3xl font-bold text-blue-600">358</p>
          <p className="text-xs text-gray-500 mt-2">+12% vs last month</p>
        </div>
        <div className="card p-6">
          <p className="text-gray-600 text-sm mb-2">Avg Clearance Time</p>
          <p className="text-3xl font-bold text-orange-600">28 min</p>
          <p className="text-xs text-gray-500 mt-2">-5% improvement</p>
        </div>
        <div className="card p-6">
          <p className="text-gray-600 text-sm mb-2">High Severity</p>
          <p className="text-3xl font-bold text-red-600">76</p>
          <p className="text-xs text-gray-500 mt-2">21% of total</p>
        </div>
        <div className="card p-6">
          <p className="text-gray-600 text-sm mb-2">Resolution Rate</p>
          <p className="text-3xl font-bold text-green-600">94%</p>
          <p className="text-xs text-gray-500 mt-2">Well above target</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <IncidentChart
          data={[
            { name: 'Mon', value: 42 },
            { name: 'Tue', value: 38 },
            { name: 'Wed', value: 51 },
            { name: 'Thu', value: 45 },
            { name: 'Fri', value: 58 },
            { name: 'Sat', value: 32 },
            { name: 'Sun', value: 28 },
          ]}
          title="Incidents by Day of Week"
          dataKey="value"
          color="#0284c7"
        />

        <IncidentChart
          data={[
            { name: '6-9 AM', value: 89 },
            { name: '9-12 PM', value: 45 },
            { name: '12-3 PM', value: 52 },
            { name: '3-6 PM', value: 76 },
            { name: '6-9 PM', value: 98 },
            { name: '9-12 AM', value: 34 },
          ]}
          title="Incidents by Time of Day"
          dataKey="value"
          color="#f59e0b"
        />

        <IncidentChart
          data={[
            { name: 'Vehicle Breakdown', value: 145 },
            { name: 'Accidents', value: 89 },
            { name: 'Tree Fall', value: 34 },
            { name: 'Water Logging', value: 23 },
            { name: 'Congestion', value: 67 },
          ]}
          title="Top Event Causes"
          dataKey="value"
          color="#ef4444"
        />

        <IncidentChart
          data={[
            { name: 'Tumkur Road', value: 42 },
            { name: 'ORR North', value: 35 },
            { name: 'Bellary Road', value: 28 },
            { name: 'Bannerghata', value: 31 },
            { name: 'Others', value: 52 },
          ]}
          title="Top Corridors"
          dataKey="value"
          color="#10b981"
        />
      </div>

      {/* Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Key Insights</h3>
          <ul className="space-y-3 text-sm text-gray-600">
            <li className="flex items-start gap-3">
              <span className="text-blue-600 font-bold">•</span>
              <span>Peak incident hours are 6-9 PM, requiring enhanced monitoring and resources</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-600 font-bold">•</span>
              <span>Vehicle breakdowns account for 40% of all incidents</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-600 font-bold">•</span>
              <span>Tumkur Road has the highest incident concentration</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-600 font-bold">•</span>
              <span>Weekend incidents are 30% lower than weekdays</span>
            </li>
          </ul>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Recommendations</h3>
          <ul className="space-y-3 text-sm text-gray-600">
            <li className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span>Increase patrol units during evening peak hours</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span>Establish vehicle breakdown assist program on major corridors</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span>Implement predictive positioning for emergency response</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-600 font-bold">✓</span>
              <span>Focus tree maintenance on high-incident zones</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
