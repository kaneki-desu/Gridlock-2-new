# TrafficTwin AI - Quick Reference Guide

## Project Overview
Full-stack traffic incident management system with ML predictions and RAG-based similarity search.

**Tech Stack**: Next.js + FastAPI + PostgreSQL + XGBoost + FAISS

---

## File Structure at a Glance

```
TrafficTwin-AI/
├── backend/                 # FastAPI application
│   ├── app.py              # Main FastAPI app
│   ├── requirements.txt
│   ├── train_model.py      # ML training script
│   ├── build_rag_index.py  # Vector indexing
│   ├── schema.sql          # Database schema
│   ├── seed_data.sql       # Test data
│   ├── db/                 # Database layer
│   ├── ml/                 # XGBoost pipeline
│   ├── rag/                # FAISS RAG system
│   ├── severity/           # Severity engine
│   ├── routes/             # API endpoints
│   └── models/             # (Generated) Trained models
│
├── frontend/               # Next.js application
│   ├── app/               # App Router structure
│   ├── components/        # React components
│   ├── lib/               # Utilities & API client
│   ├── public/            # Static assets
│   └── package.json
│
├── README.md              # Main documentation
├── API_DOCUMENTATION.md   # API reference
├── ARCHITECTURE.md        # System design
├── DEPLOYMENT.md          # Deployment guide
├── setup.sh / setup.bat   # Automated setup
└── QUICK_REFERENCE.md     # This file
```

---

## Quick Commands

### Setup
```bash
# Automated setup (Linux/macOS)
bash setup.sh

# Automated setup (Windows)
setup.bat

# Manual setup
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Training Models
```bash
cd backend

# Train XGBoost
python train_model.py --data-path /path/to/data.csv

# Build FAISS index
python build_rag_index.py --data-path /path/to/data.csv
```

### Running Services
```bash
# Backend (port 8000)
cd backend && python app.py

# Frontend (port 3000)
cd frontend && npm run dev

# Database
createdb traffic_twin_ai
psql traffic_twin_ai < backend/schema.sql
```

### Database
```bash
# Load sample data
psql traffic_twin_ai < backend/seed_data.sql

# Reset database
dropdb traffic_twin_ai
createdb traffic_twin_ai
psql traffic_twin_ai < backend/schema.sql
```

---

## API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/incident` | Submit incident |
| GET | `/incident/{id}` | Get incident details |
| GET | `/incidents` | List incidents |
| POST | `/predict-clearance` | Predict time |
| POST | `/calculate-severity` | Calculate severity |
| POST | `/retrieve-similar` | Find similar cases |
| POST | `/recommend` | Get recommendations |
| POST | `/resolve-incident/{id}` | Resolve incident |
| GET | `/health` | Health check |

---

## Core Features

### 1. Incident Management
- Submit incidents with full details
- Track status (active/closed/resolved)
- Retrieve historical data

### 2. ML Prediction (XGBoost)
- Input: 10 features (type, cause, location, priority, etc.)
- Output: Predicted clearance time (minutes)
- Confidence level based on prediction range

### 3. Severity Calculation
- Multi-factor scoring (6 components)
- Classification: Low (0-6), Medium (7-12), High (13+)
- Diversion recommendation logic

### 4. RAG System
- Semantic similarity search
- Sentence Transformer embeddings
- FAISS vector database
- Returns top 5 similar incidents

### 5. Recommendations
- Combines severity, prediction, history
- Suggests actions for traffic management
- Urgency levels: Normal, High, Critical

---

## Incident Submission Flow

```
User Form Input
    ↓
API Validation (Pydantic)
    ↓
Store in PostgreSQL
    ↓
├─ Predict clearance time (XGBoost)
├─ Calculate severity (Rules)
├─ Retrieve similar incidents (FAISS)
└─ Generate recommendations
    ↓
Return results to frontend
```

---

## Key Data Models

### TrafficIncident
```python
{
  "id": 1,
  "event_type": "unplanned",
  "event_cause": "vehicle_breakdown",
  "latitude": 13.04,
  "longitude": 77.51,
  "corridor": "Tumkur Road",
  "priority": "High",
  "status": "active",
  "start_datetime": "2024-01-15T10:30:00Z"
}
```

### Prediction
```python
{
  "predicted_clearance_time": 42.5,
  "confidence": "High"  # High|Medium|Low
}
```

### Severity
```python
{
  "severity_score": 14.5,
  "severity_level": "High"  # Low|Medium|High
}
```

### Recommendation
```python
{
  "severity": "High",
  "predicted_clearance": 42,
  "diversion_required": true,
  "urgency_level": "Critical",  # Normal|High|Critical
  "similar_cases_found": 5
}
```

---

## Configuration Files

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/traffic_twin_ai
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Feature Matrix

| Feature | Component | Status |
|---------|-----------|--------|
| Incident Form | Frontend (IncidentForm.tsx) | ✅ |
| Real-time Prediction | Backend (ml/) + Frontend | ✅ |
| Severity Calculation | Backend (severity/) | ✅ |
| Similar Case Retrieval | Backend (rag/) | ✅ |
| Recommendation Engine | Backend (routes/) | ✅ |
| Dashboard | Frontend (app/page.tsx) | ✅ |
| Incidents List | Frontend (app/incidents/) | ✅ |
| Analytics | Frontend (app/analytics/) | ✅ |
| Interactive Map | Frontend (IncidentMap.tsx) | ✅ |
| Charts & Visualization | Frontend (IncidentChart.tsx) | ✅ |

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | Kill process: `lsof -i :8000 \| awk 'NR!=1 {print $2}' \| xargs kill -9` |
| Module not found | Run `pip install -r requirements.txt` or `npm install` |
| Database connection error | Check DATABASE_URL in .env, verify PostgreSQL is running |
| Model not found | Train model: `python train_model.py --data-path data.csv` |
| CORS error | Update API_URL in frontend .env |
| Build fails | Clear cache: `rm -rf .next` and reinstall: `npm install` |

---

## Performance Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| Incident submission | <500ms | 200ms |
| Prediction | <20ms | 5-10ms |
| Severity calculation | <10ms | 1-2ms |
| Similarity search | <10ms | 3-5ms |
| Page load | <2s | 1.5s |
| API response | <1s | 200-400ms |

---

## Testing Checklist

- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Database created and migrated
- [ ] ML models trained
- [ ] FAISS index built
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] API health check passes
- [ ] Incident form submission works
- [ ] Predictions appear in results
- [ ] Similar cases display
- [ ] Analytics load correctly
- [ ] Map renders incidents

---

## Next Steps for Development

### Short Term
- [ ] Integrate authentication
- [ ] Add rate limiting
- [ ] Implement caching
- [ ] Add unit tests
- [ ] Set up CI/CD

### Medium Term
- [ ] Deploy to cloud
- [ ] Add more ML models
- [ ] Implement real-time updates (WebSocket)
- [ ] Add mobile app
- [ ] Expand to more cities

### Long Term
- [ ] Multi-tenant support
- [ ] Advanced analytics
- [ ] Integration with traffic signals
- [ ] Autonomous recommendations
- [ ] Predictive incident prevention

---

## Useful Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [XGBoost Guide](https://xgboost.readthedocs.io/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [PostgreSQL Manual](https://www.postgresql.org/docs/)
- [Sentence Transformers](https://www.sbert.net/)

---

## Support & Contact

For issues:
1. Check API docs at `/docs` (Swagger)
2. Review browser console for frontend errors
3. Check server logs for backend errors
4. Consult README.md for detailed info

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
