'use client';

import React, { useEffect, useState } from 'react';
import { submitIncident, IncidentInput, IncidentResponse } from '@/lib/api';
import { AlertCircle, Loader } from 'lucide-react';

interface Props {
  onIncidentSubmitted: (incident: IncidentInput, response: IncidentResponse) => void;
}

const STORAGE_KEY = 'trafficTwinIncidentForm';

const defaultFormData: IncidentInput = {
  event_type: 'unplanned',
  event_cause: 'vehicle_breakdown',
  latitude: 13.0400041,
  longitude: 77.5180991,
  corridor: 'Tumkur Road',
  zone: 'North Zone 1',
  junction: 'JalahaliCross',
  priority: 'High',
  requires_road_closure: false,
  vehicle_type: 'lcv',
  address: 'Tumkur Road, Bengaluru',
  description: '',
  start_datetime: new Date().toISOString().slice(0, 16),
};

export default function IncidentForm({ onIncidentSubmitted }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<IncidentInput>(defaultFormData);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as IncidentInput;
        setFormData({
          ...defaultFormData,
          ...parsed,
          start_datetime: parsed.start_datetime || defaultFormData.start_datetime,
        });
      } catch {
        setFormData(defaultFormData);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(formData));
  }, [formData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, type, value } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await submitIncident(formData);
      onIncidentSubmitted(formData, result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit incident');
      console.error('Error submitting incident:', err);
    } finally {
      setLoading(false);
    }
  };

  const eventCauses = [
    'vehicle_breakdown',
    'accident',
    'tree_fall',
    'water_logging',
    'pot_holes',
    'congestion',
    'construction',
    'public_event',
    'others',
  ];

  const vehicleTypes = [
    'lcv',
    'heavy_vehicle',
    'bmtc_bus',
    'ksrtc_bus',
    'private_bus',
    'private_car',
    'unknown',
  ];

  const corridors = [
    'Tumkur Road',
    'ORR North 1',
    'ORR North 2',
    'ORR East 1',
    'ORR East 2',
    'ORR West 1',
    'Bellary Road 1',
    'Bellary Road 2',
    'Bannerghata Road',
    'Hosur Road',
    'Magadi Road',
    'Old Madras Road',
    'CBD 2',
    'Non-corridor',
  ];

  return (
    <form onSubmit={handleSubmit} className="card p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Report Traffic Incident</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md flex gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Event Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Event Type</label>
          <select
            name="event_type"
            value={formData.event_type}
            onChange={handleChange}
            className="input-field"
          >
            <option value="planned">Planned</option>
            <option value="unplanned">Unplanned</option>
          </select>
        </div>

        {/* Event Cause */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Event Cause</label>
          <select
            name="event_cause"
            value={formData.event_cause}
            onChange={handleChange}
            className="input-field"
          >
            {eventCauses.map((cause) => (
              <option key={cause} value={cause}>
                {cause.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Latitude */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Latitude</label>
          <input
            type="number"
            name="latitude"
            value={formData.latitude}
            onChange={handleChange}
            step="0.0001"
            className="input-field"
          />
        </div>

        {/* Longitude */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Longitude</label>
          <input
            type="number"
            name="longitude"
            value={formData.longitude}
            onChange={handleChange}
            step="0.0001"
            className="input-field"
          />
        </div>

        {/* Corridor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Corridor</label>
          <select
            name="corridor"
            value={formData.corridor || ''}
            onChange={handleChange}
            className="input-field"
          >
            <option value="">Select Corridor</option>
            {corridors.map((corridor) => (
              <option key={corridor} value={corridor}>
                {corridor}
              </option>
            ))}
          </select>
        </div>

        {/* Zone */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Zone</label>
          <input
            type="text"
            name="zone"
            value={formData.zone || ''}
            onChange={handleChange}
            className="input-field"
            placeholder="e.g., North Zone 1"
          />
        </div>

        {/* Junction */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Junction</label>
          <input
            type="text"
            name="junction"
            value={formData.junction || ''}
            onChange={handleChange}
            className="input-field"
            placeholder="e.g., JalahaliCross"
          />
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
          <select
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            className="input-field"
          >
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>

        {/* Vehicle Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Vehicle Type</label>
          <select
            name="vehicle_type"
            value={formData.vehicle_type || ''}
            onChange={handleChange}
            className="input-field"
          >
            <option value="">Select Vehicle Type</option>
            {vehicleTypes.map((type) => (
              <option key={type} value={type}>
                {type.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Address */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
          <input
            type="text"
            name="address"
            value={formData.address || ''}
            onChange={handleChange}
            className="input-field"
            placeholder="Full address of incident"
          />
        </div>

        {/* Description */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            name="description"
            value={formData.description || ''}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, description: e.target.value }))
            }
            rows={4}
            className="input-field resize-none"
            placeholder="Additional incident details..."
          />
        </div>

        {/* Start Date / Time */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Start Date & Time</label>
          <input
            type="datetime-local"
            name="start_datetime"
            value={formData.start_datetime || ''}
            onChange={handleChange}
            className="input-field"
          />
        </div>

        {/* Road Closure */}
        <div className="md:col-span-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              name="requires_road_closure"
              checked={formData.requires_road_closure}
              onChange={handleChange}
              className="w-4 h-4"
            />
            <span className="text-sm font-medium text-gray-700">Requires Road Closure</span>
          </label>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader size={20} className="animate-spin" />
            Submitting...
          </>
        ) : (
          'Submit Incident'
        )}
      </button>
    </form>
  );
}
