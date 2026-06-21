# TrafficTwin AI - API Documentation

## Overview
TrafficTwin AI provides a comprehensive REST API for traffic incident management, powered by machine learning predictions and RAG-based similarity search.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, all endpoints are public. In production, implement JWT or OAuth2 authentication.

## Endpoints

### 1. Incident Management

#### Submit New Incident
**Endpoint**: `POST /incident`

**Description**: Submit a new traffic incident with automatic prediction and severity calculation.

**Request Body**:
```json
{
  "event_type": "unplanned",
  "event_cause": "vehicle_breakdown",
  "latitude": 13.0400041,
  "longitude": 77.5180991,
  "corridor": "Tumkur Road",
  "zone": "North Zone 1",
  "junction": "JalahaliCross",
  "priority": "High",
  "requires_road_closure": false,
  "vehicle_type": "lcv",
  "address": "Tumkur Road, Bengaluru"
}
```

**Response** (201):
```json
{
  "incident_id": 1,
  "status": "created",
  "severity": "High",
  "predicted_clearance": 42.5,
  "diversion_required": true,
  "urgency_level": "Critical",
  "similar_cases_found": 5
}
```

**Error Response** (400):
```json
{
  "detail": "Error creating incident: <error message>"
}
```

#### Get Incident Details
**Endpoint**: `GET /incident/{incident_id}`

**Description**: Retrieve details of a specific incident.

**Parameters**:
- `incident_id` (path, integer, required): Incident ID

**Response** (200):
```json
{
  "id": 1,
  "event_type": "unplanned",
  "event_cause": "vehicle_breakdown",
  "latitude": 13.0400041,
  "longitude": 77.5180991,
  "corridor": "Tumkur Road",
  "zone": "North Zone 1",
  "junction": "JalahaliCross",
  "priority": "High",
  "requires_road_closure": false,
  "vehicle_type": "lcv",
  "address": "Tumkur Road, Bengaluru",
  "start_datetime": "2024-01-15T10:30:00Z",
  "closed_datetime": null,
  "status": "active",
  "actual_clearance_time_minutes": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### List All Incidents
**Endpoint**: `GET /incidents`

**Description**: Retrieve a paginated list of incidents with optional filtering.

**Query Parameters**:
- `skip` (integer, optional, default=0): Number of records to skip
- `limit` (integer, optional, default=100): Number of records to return
- `status` (string, optional): Filter by status (active/closed/resolved)

**Response** (200):
```json
[
  {
    "id": 1,
    "event_type": "unplanned",
    "event_cause": "vehicle_breakdown",
    ...
  },
  ...
]
```

#### Resolve Incident
**Endpoint**: `POST /resolve-incident/{incident_id}`

**Description**: Mark an incident as resolved and update RAG system with actual data.

**Parameters**:
- `incident_id` (path, integer, required): Incident ID

**Request Body**:
```json
{
  "actual_clearance_time": 45
}
```

**Response** (200):
```json
{
  "incident_id": 1,
  "status": "resolved",
  "actual_clearance_time": 45,
  "message": "Incident resolved and learning systems updated"
}
```

---

### 2. Predictions

#### Predict Clearance Time
**Endpoint**: `POST /predict-clearance`

**Description**: Predict clearance time for an incident using XGBoost model.

**Request Body**:
```json
{
  "event_type": "unplanned",
  "event_cause": "vehicle_breakdown",
  "latitude": 13.0400041,
  "longitude": 77.5180991,
  "corridor": "Tumkur Road",
  "priority": "High",
  "requires_road_closure": false,
  "vehicle_type": "lcv"
}
```

**Response** (200):
```json
{
  "predicted_clearance_time": 42.5,
  "confidence": "High"
}
```

**Confidence Levels**:
- `High`: < 15 minutes
- `Medium`: 15-45 minutes
- `Low`: > 45 minutes

---

### 3. Severity

#### Calculate Severity
**Endpoint**: `POST /calculate-severity`

**Description**: Calculate severity score for an incident.

**Request Body**:
```json
{
  "event_type": "unplanned",
  "event_cause": "vehicle_breakdown",
  "latitude": 13.0400041,
  "longitude": 77.5180991,
  "corridor": "Tumkur Road",
  "priority": "High",
  "requires_road_closure": true,
  "vehicle_type": "heavy_vehicle"
}
```

**Response** (200):
```json
{
  "severity_score": 14.5,
  "severity_level": "High"
}
```

**Severity Levels**:
- `Low`: 0-6
- `Medium`: 7-12
- `High`: 13+

---

### 4. RAG Retrieval

#### Retrieve Similar Incidents
**Endpoint**: `POST /retrieve-similar`

**Description**: Find historically similar incidents using semantic similarity.

**Request Body**:
```json
{
  "event_type": "unplanned",
  "event_cause": "vehicle_breakdown",
  "latitude": 13.0400041,
  "longitude": 77.5180991,
  "corridor": "Tumkur Road",
  "priority": "High"
}
```

**Response** (200):
```json
[
  {
    "incident_id": 101,
    "similarity_score": 0.92,
    "summary": "Vehicle breakdown on Tumkur Road during peak hour, high priority, heavy vehicle, resolved in 42 minutes."
  },
  {
    "incident_id": 102,
    "similarity_score": 0.87,
    "summary": "LCV breakdown on Tumkur Road, high priority, resolved in 45 minutes."
  },
  ...
]
```

---

### 5. Recommendations

#### Get Recommendations
**Endpoint**: `POST /recommend`

**Description**: Get comprehensive recommendations combining severity, predictions, and similar cases.

**Request Body**:
```json
{
  "event_type": "unplanned",
  "event_cause": "vehicle_breakdown",
  "latitude": 13.0400041,
  "longitude": 77.5180991,
  "corridor": "Tumkur Road",
  "priority": "High",
  "requires_road_closure": false,
  "vehicle_type": "lcv"
}
```

**Response** (200):
```json
{
  "severity": "High",
  "predicted_clearance": 42,
  "diversion_required": true,
  "urgency_level": "Critical",
  "similar_cases_found": 5,
  "estimated_resolution_time": 42
}
```

**Urgency Levels**:
- `Normal`: Low severity + < 30 min predicted time
- `High`: Medium severity or 30-60 min predicted time
- `Critical`: High severity or > 60 min predicted time

---

### 6. Health & Status

#### Health Check
**Endpoint**: `GET /health`

**Response** (200):
```json
{
  "status": "healthy",
  "service": "TrafficTwin AI Backend"
}
```

#### API Root
**Endpoint**: `GET /`

**Response** (200):
```json
{
  "service": "TrafficTwin AI",
  "version": "1.0.0",
  "description": "Adaptive traffic intelligence system",
  "docs": "/docs",
  "endpoints": {
    "POST /incident": "Submit new incident",
    "POST /predict-clearance": "Predict clearance time",
    ...
  }
}
```

---

## Request/Response Formats

### Common Headers
```
Content-Type: application/json
```

### Error Handling

All errors return appropriate HTTP status codes:

- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently not implemented. Production deployment should include:
- Rate limiting per IP/user
- Request throttling
- Queue management for long-running tasks

---

## Data Types

### Event Type
- `planned`
- `unplanned`

### Event Causes
- `vehicle_breakdown`
- `accident`
- `tree_fall`
- `water_logging`
- `pot_holes`
- `congestion`
- `construction`
- `public_event`
- `others`

### Priority Levels
- `Low`
- `Medium`
- `High`

### Vehicle Types
- `lcv` (Light Commercial Vehicle)
- `heavy_vehicle`
- `bmtc_bus` (BMTC City Bus)
- `ksrtc_bus` (KSRTC State Bus)
- `private_bus`
- `private_car`
- `unknown`

### Status
- `active`: Currently ongoing
- `closed`: Traffic cleared but not marked resolved
- `resolved`: Complete with actual data recorded

---

## Example Workflows

### Workflow 1: Report and Track Incident
```
1. POST /incident → Get incident_id and predictions
2. GET /incident/{id} → Check current status
3. Wait for incident resolution
4. POST /resolve-incident/{id} → Mark resolved with actual time
```

### Workflow 2: Get Insights Before Action
```
1. POST /calculate-severity → Assess impact
2. POST /predict-clearance → Estimate resolution time
3. POST /retrieve-similar → Learn from history
4. POST /recommend → Get action items
```

### Workflow 3: Real-time Dashboard
```
1. GET /incidents → Fetch all incidents
2. For each incident:
   - GET /incident/{id} → Get details
   - Use previous severity/prediction data
3. Refresh periodically (e.g., every 30 seconds)
```

---

## Performance Tips

1. **Batch Operations**: Handle multiple incidents efficiently
2. **Caching**: Cache predictions for identical inputs
3. **Pagination**: Always use limit/skip for list endpoints
4. **Async Processing**: Consider async job queue for large operations
5. **Connection Pooling**: Reuse DB connections

---

## Testing with curl

```bash
# Submit incident
curl -X POST http://localhost:8000/incident \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "unplanned",
    "event_cause": "vehicle_breakdown",
    "latitude": 13.0400,
    "longitude": 77.5180,
    "corridor": "Tumkur Road",
    "priority": "High",
    "requires_road_closure": false,
    "vehicle_type": "lcv"
  }'

# Get incident
curl http://localhost:8000/incident/1

# Get recommendations
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{...incident data...}'

# List incidents
curl "http://localhost:8000/incidents?status=active&limit=10"
```

---

## Interactive Documentation

Access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These auto-generated docs allow you to test endpoints directly from the browser.

---

**Last Updated**: 2024-01-15
