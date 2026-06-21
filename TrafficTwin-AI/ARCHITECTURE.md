# TrafficTwin AI - Architecture & Design Document

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         Next.js Frontend Dashboard (Port 3000)              │  │
│  │  - Incident form, results display, analytics, real-time map│  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ REST API Calls (JSON)
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API Layer                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │      FastAPI Backend (Port 8000)                            │  │
│  │  - Request validation, routing, error handling             │  │
│  │  - CORS middleware for cross-origin requests               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
┌──────────────┐  ┌─────────┐  ┌─────────────┐
│  Prediction  │  │Severity │  │     RAG     │
│   Pipeline   │  │ Engine  │  │  Retriever  │
└──────────────┘  └─────────┘  └─────────────┘
         │             │             │
         └─────────────┼─────────────┘
                       ▼
┌──────────────────────────────────────────────┐
│        Machine Learning & Analytics          │
│ ┌──────────────┐         ┌──────────────┐   │
│ │ XGBoost Model│         │ FAISS Index  │   │
│ │ (pkl file)   │         │ (pkl file)   │   │
│ └──────────────┘         └──────────────┘   │
└──────────────────────────────────────────────┘
         │                         │
         └─────────────┬───────────┘
                       ▼
┌──────────────────────────────────────────────┐
│         Persistent Storage Layer             │
│ ┌────────────────────────────────────────┐  │
│ │   PostgreSQL Database                  │  │
│ │  - Incidents, predictions, severity   │  │
│ │  - Similar relationships, recommendations│
│ └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Frontend (Next.js)
**Technology**: React 18, Next.js 14, TailwindCSS, Recharts, Leaflet
**Responsibilities**:
- User-facing incident submission form
- Real-time results visualization
- Interactive dashboard with charts and maps
- Historical incident browsing
- Analytics and insights display

**Key Pages**:
- `/`: Main dashboard
- `/incidents`: Incidents list
- `/analytics`: Analytics dashboard

**Key Components**:
- `IncidentForm`: Handles user input
- `ResultCards`: Displays predictions
- `IncidentChart`: Data visualization
- `IncidentMap`: Geographic visualization
- `SimilarIncidents`: Historical context

### 2. Backend API (FastAPI)
**Technology**: FastAPI, Uvicorn, SQLAlchemy, Pydantic
**Responsibilities**:
- Request validation and routing
- Business logic orchestration
- Database operations
- Error handling and logging

**Key Routes** (routes/incidents.py):
- `POST /incident`: Submit incident
- `POST /predict-clearance`: ML prediction
- `POST /calculate-severity`: Rule-based scoring
- `POST /retrieve-similar`: RAG search
- `POST /recommend`: Integrated recommendations
- `POST /resolve-incident/{id}`: Update learning
- `GET /incident/{id}`, `GET /incidents`: Query incidents

### 3. Prediction Engine (ML)
**Technology**: XGBoost, scikit-learn, pickle
**Location**: `backend/ml/preprocessor.py`
**Responsibilities**:
- Data preprocessing and encoding
- Feature engineering (peak hour extraction)
- Model training on historical data
- Real-time prediction inference

**Features**:
```
Input Features:
- event_type (categorical)
- event_cause (categorical)
- latitude (continuous)
- longitude (continuous)
- corridor (categorical)
- priority (categorical)
- requires_road_closure (boolean)
- vehicle_type (categorical)
- junction (categorical)
- peak_hour (binary)

Target Variable:
- clearance_time (continuous, minutes)
```

**Model Details**:
- Algorithm: XGBoost Regressor
- Tree booster with L2 regularization
- Learning rate: 0.1
- Estimators: 100
- Max depth: 6

### 4. Severity Engine
**Technology**: Python rules engine
**Location**: `backend/severity/engine.py`
**Responsibilities**:
- Multi-factor severity scoring
- Urgency level calculation
- Diversion recommendation logic

**Scoring System**:
```
Severity Score = 
  Priority Weight (2-8) +
  Road Closure Weight (0-3) +
  Corridor Weight (1-2.5) +
  Vehicle Weight (0.5-2.5) +
  Peak Hour Weight (0-2) +
  Junction Weight (0-1.5)

Total Range: 0-19 points
Levels:
- Low: 0-6
- Medium: 7-12
- High: 13+
```

### 5. RAG System (Retrieval-Augmented Generation)
**Technology**: Sentence Transformers, FAISS, Python
**Location**: `backend/rag/retriever.py`
**Responsibilities**:
- Convert incidents to text summaries
- Generate semantic embeddings
- Store and retrieve similar incidents
- Update knowledge base with resolved cases

**Process Flow**:
```
1. Incident Data
   ↓
2. Summary Generation
   "Vehicle breakdown on Tumkur Road during peak hour..."
   ↓
3. Embedding (384-dim vector)
   Via Sentence Transformer (all-MiniLM-L6-v2)
   ↓
4. Similarity Search
   FAISS L2 distance search
   ↓
5. Top 5 Similar Cases
   With similarity scores
```

### 6. Database Layer
**Technology**: PostgreSQL, SQLAlchemy ORM
**Location**: `backend/db/`

**Schema**:
```sql
traffic_incidents
├── id (PK)
├── event details (type, cause, location)
├── incident attributes (priority, vehicle, road closure)
├── timestamps (start, closed, resolved)
├── status tracking
└── clearance time (actual)

prediction_results
├── id (PK)
├── incident_id (FK)
├── predicted_clearance_time
└── supporting features

severity_scores
├── id (PK)
├── incident_id (FK)
├── severity_score
├── severity_level
└── component weights

similar_incidents
├── id (PK)
├── query_incident_id (FK)
├── similar_incident_id (FK)
└── similarity_score

incident_recommendations
├── id (PK)
├── incident_id (FK)
├── severity, clearance, urgency
└── action items
```

## Data Flow

### Submit Incident Flow
```
User Submits Form
    ↓
API Validates Input (Pydantic)
    ↓
Store in PostgreSQL
    ↓
Run in Parallel:
  ├─→ XGBoost Prediction
  │   └─→ Store in prediction_results
  ├─→ Severity Calculation
  │   └─→ Store in severity_scores
  ├─→ RAG Retrieval
  │   └─→ Store in similar_incidents
  └─→ Generate Recommendations
      └─→ Store in incident_recommendations
    ↓
Return Results to Frontend
```

### Resolve Incident Flow
```
User Reports Resolution
    ↓
Update incident status
    ↓
Calculate actual clearance time
    ↓
Generate Summary Text
    ↓
Create Embedding
    ↓
Add to FAISS Index
    ↓
Update Learning Systems
```

## Scalability Considerations

### Current Design (Development)
- Single FastAPI instance
- Local FAISS index
- PostgreSQL on localhost
- Suitable for: Testing, demos, small deployments

### Production Scalability Options

1. **Horizontal Scaling**
   - Load balancer (nginx, AWS ALB)
   - Multiple FastAPI instances
   - Connection pooling (pgBouncer)
   - Caching layer (Redis)

2. **Vector DB Scaling**
   - Distributed FAISS with sharding
   - Managed vector DB (Pinecone, Weaviate)
   - Periodic batch indexing

3. **ML Model Serving**
   - TensorFlow Serving / BentoML
   - Model versioning and A/B testing
   - GPU acceleration for predictions
   - Batch prediction queue

4. **Async Processing**
   - Celery + Redis for background jobs
   - Kafka for event streaming
   - Delayed indexing for large batches

## Technology Decisions & Rationale

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend Framework | Next.js | SSR, optimal performance, TypeScript support |
| UI Framework | TailwindCSS | Utility-first, responsive, fast development |
| Charts | Recharts | React-native, responsive, customizable |
| Maps | Leaflet + react-leaflet | Lightweight, free tiles, good OSM integration |
| Backend Framework | FastAPI | High performance, auto-docs, type validation |
| ORM | SQLAlchemy | SQL flexibility, relationship management |
| Database | PostgreSQL | ACID, spatial queries (PostGIS), reliability |
| ML Model | XGBoost | Gradient boosting, handles mixed features, proven |
| Embeddings | Sentence Transformers | Fast, accurate, pre-trained models |
| Vector DB | FAISS | Fast similarity search, lightweight, free |
| Serialization | Pickle | Python-native, preserves all object state |

## Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Incident submission (end-to-end) | ~200ms | Parallel processing |
| XGBoost prediction | 5-10ms | Cached model |
| Severity calculation | 1-2ms | Rule-based, no I/O |
| FAISS similarity search (5 cases) | 3-5ms | Index in memory |
| Database write | 10-20ms | PostgreSQL roundtrip |
| Frontend page load | <2s | Initial, cached assets |

## Error Handling Strategy

### API Level
- Pydantic validation for input types
- HTTPException for business logic errors
- Global exception handler for unhandled errors
- Detailed error messages for debugging

### Database Level
- Connection pooling with retry logic
- Transaction rollback on error
- Foreign key constraints
- Index coverage for queries

### ML Level
- Model availability check at startup
- Graceful degradation if FAISS unavailable
- Fallback predictions if encoding fails
- Logging of prediction confidence

## Monitoring & Logging

**Recommended Additions** (Production):
- Structured logging (Python logging module)
- Metrics collection (Prometheus)
- Error tracking (Sentry)
- APM (Application Performance Monitoring)
- Database query monitoring
- ML model drift detection

## Security Considerations

**Current Implementation**:
- All endpoints public (development)
- No authentication/authorization
- No rate limiting
- No input sanitization (Pydantic handles type safety)

**Production Recommendations**:
- JWT/OAuth2 authentication
- Role-based access control
- Rate limiting per IP/user
- CORS configuration restrictions
- HTTPS/TLS enforcement
- SQL injection prevention (via SQLAlchemy)
- CSRF protection (if applicable)
- API key management
- Audit logging

## Testing Strategy

### Unit Tests
- ML model preprocessing
- Severity calculation rules
- Utility functions

### Integration Tests
- API endpoints with mock database
- Database operations
- ML model inference

### End-to-End Tests
- Frontend form submission
- API response validation
- Database state verification

## Deployment Architecture

### Development
```
Local Machine
├── Backend: uvicorn (reload enabled)
├── Frontend: next dev (hot reload)
└── Database: localhost PostgreSQL
```

### Production
```
Cloud Infrastructure
├── Frontend: Vercel/Netlify (CDN)
├── Backend: Docker container (ECS/AKS/GKE)
├── Database: Managed PostgreSQL (RDS/CloudSQL)
├── Vector DB: Distributed or managed service
└── Cache: Redis cluster
```

## Backup & Disaster Recovery

**Database**:
- Daily automated backups
- Point-in-time recovery capability
- Replication for high availability

**ML Models**:
- Version control in git
- Backup artifacts in object storage
- Checksums for integrity

**Vector Index**:
- Periodic snapshots
- Rebuild capability from raw data
- Version tracking

---

**Last Updated**: 2024-01-15
**Maintainer**: Traffic Intelligence Team
