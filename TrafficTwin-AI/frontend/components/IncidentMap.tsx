'use client';

import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface MapMarker {
  id: number;
  latitude: number;
  longitude: number;
  severity: string;
  eventCause: string;
}

interface IncidentMapProps {
  incidents: MapMarker[];
}

// Fix default icon issue
const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const getSeverityIcon = (severity: string) => {
  const color =
    severity === 'High'
      ? '#ef4444'
      : severity === 'Medium'
      ? '#f59e0b'
      : '#10b981';

  return L.icon({
    iconUrl: `data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='${encodeURIComponent(color)}'><path d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z'/></svg>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
};

export default function IncidentMap({ incidents }: IncidentMapProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="h-96 bg-gray-100 rounded-md animate-pulse" />;

  // Default center (Bengaluru)
  const defaultCenter: [number, number] = [13.0827, 77.5979];

  return (
    <div className="card overflow-hidden">
      <MapContainer center={defaultCenter} zoom={12} style={{ height: '400px', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        {incidents.map((incident) => (
          <Marker
            key={incident.id}
            position={[incident.latitude, incident.longitude]}
            icon={getSeverityIcon(incident.severity)}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-bold">{incident.eventCause.replace(/_/g, ' ')}</h4>
                <p className="text-sm text-gray-600">Severity: {incident.severity}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
