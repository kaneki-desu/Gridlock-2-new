import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface IncidentInput {
  event_type: string;
  event_cause: string;
  latitude: number;
  longitude: number;
  corridor?: string;
  zone?: string;
  junction?: string;
  priority: string;
  requires_road_closure: boolean;
  vehicle_type?: string;
  address?: string;
  description?: string;
  start_datetime?: string;
}

export interface IncidentResponse {
  incident_id: number;
  status: string;
  severity: string;
  predicted_clearance: number;
  diversion_required: boolean;
  urgency_level: string;
  similar_cases_found: number;
  llm_suggestions?: string;
}

export interface RecommendationResponse {
  severity: string;
  predicted_clearance: number;
  diversion_required: boolean;
  urgency_level: string;
  similar_cases_found: number;
  estimated_resolution_time: number;
}

// Submit a new incident
export async function submitIncident(data: IncidentInput): Promise<IncidentResponse> {
  const response = await api.post<IncidentResponse>('/incident', data);
  return response.data;
}

// Predict clearance time
export async function predictClearance(data: IncidentInput) {
  const response = await api.post('/predict-clearance', data);
  return response.data;
}

// Calculate severity
export async function calculateSeverity(data: IncidentInput) {
  const response = await api.post('/calculate-severity', data);
  return response.data;
}

// Retrieve similar incidents
export async function retrieveSimilar(data: IncidentInput) {
  const response = await api.post('/retrieve-similar', data);
  return response.data;
}

// Get recommendations
export async function getRecommendations(data: IncidentInput): Promise<RecommendationResponse> {
  const response = await api.post<RecommendationResponse>('/recommend', data);
  return response.data;
}

// Get incident details
export async function getIncident(id: number) {
  const response = await api.get(`/incident/${id}`);
  return response.data;
}

// Get list of incidents
export async function listIncidents(skip = 0, limit = 100, status?: string) {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });
  if (status) {
    params.append('status', status);
  }
  const response = await api.get(`/incidents?${params}`);
  return response.data;
}

// Resolve incident
export async function resolveIncident(id: number, actualClearanceTime: number) {
  const response = await api.post(`/resolve-incident/${id}`, {
    actual_clearance_time: actualClearanceTime,
  });
  return response.data;
}

export async function updateIncidentStatus(id: number, status: string) {
  const response = await api.post('/update-incident-status', {
    incident_id: id,
    status,
  });
  return response.data;
}

export default api;
