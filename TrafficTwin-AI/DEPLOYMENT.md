# TrafficTwin AI - Deployment Guide

## Local Development

### Quick Start (Windows)
```batch
cd TrafficTwin-AI
setup.bat
```

### Quick Start (macOS/Linux)
```bash
cd TrafficTwin-AI
bash setup.sh
```

### Manual Setup

1. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with database credentials
   python train_model.py --data-path ../path/to/data.csv
   python build_rag_index.py --data-path ../path/to/data.csv
   python app.py
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Database**
   ```bash
   createdb traffic_twin_ai
   psql traffic_twin_ai < backend/schema.sql
   psql traffic_twin_ai < backend/seed_data.sql  # Optional: load test data
   ```

---

## Docker Deployment

### Build Docker Images

**Backend Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["python", "app.py"]
```

**Frontend Dockerfile**:
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY frontend/package.json .
EXPOSE 3000
CMD ["npm", "start"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: traffic_twin_ai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/schema.sql:/docker-entrypoint-initdb.d/schema.sql

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/traffic_twin_ai
    depends_on:
      - postgres
    volumes:
      - ./backend/models:/app/models

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

**Run**:
```bash
docker-compose up -d
```

---

## Cloud Deployment

### AWS Deployment

1. **RDS for PostgreSQL**
   - Create database instance
   - Update backend DATABASE_URL

2. **ECS/Fargate for Backend**
   - Push image to ECR
   - Create ECS task definition
   - Configure service with load balancer

3. **Vercel for Frontend**
   ```bash
   npm install -g vercel
   cd frontend
   vercel deploy
   ```

### Google Cloud Deployment

1. **Cloud SQL for PostgreSQL**
   - Create instance and database

2. **Cloud Run for Backend**
   ```bash
   gcloud run deploy traffic-twin-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Cloud Build for CI/CD**
   - Configure cloudbuild.yaml
   - Set up triggers on git push

### Azure Deployment

1. **Azure Database for PostgreSQL**
   - Create server and database

2. **App Service for Backend**
   - Create App Service
   - Configure deployment from git

3. **Static Web Apps for Frontend**
   - Connect GitHub repo
   - Configure build settings

---

## Production Configuration

### Environment Variables

**Backend (.env)**:
```
DATABASE_URL=postgresql://user:pass@prod-db:5432/traffic_twin_ai
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://traffictwin.example.com
JWT_SECRET=your-secret-key-here
MODEL_PATH=/models/xgboost_model.pkl
ENCODERS_PATH=/models/encoders.pkl
FAISS_INDEX_PATH=/models/faiss_index.pkl
```

**Frontend (.env.production)**:
```
NEXT_PUBLIC_API_URL=https://api.traffictwin.example.com
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

### Security Hardening

1. **FastAPI**
   ```python
   # Add to app.py
   from fastapi.security import HTTPBearer
   from fastapi import Depends
   
   security = HTTPBearer()
   
   @app.post("/incident")
   async def submit_incident(
       incident: IncidentInput,
       credentials: HTTPAuthCredentials = Depends(security)
   ):
       # Verify token
       token = verify_jwt(credentials.credentials)
       ...
   ```

2. **CORS Configuration**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://traffictwin.example.com"],
       allow_credentials=True,
       allow_methods=["POST", "GET"],
       allow_headers=["*"],
   )
   ```

3. **Rate Limiting**
   ```bash
   pip install slowapi
   ```
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/incident")
   @limiter.limit("10/minute")
   async def submit_incident(...):
       ...
   ```

4. **HTTPS/TLS**
   - Use reverse proxy (nginx)
   - Obtain SSL certificate (Let's Encrypt)
   - Redirect HTTP to HTTPS

5. **Database Security**
   - Strong passwords
   - Restrict connection IPs
   - Enable SSL connections
   - Regular backups
   - Encryption at rest

### Monitoring & Logging

1. **Structured Logging**
   ```python
   import logging
   import json
   
   class JSONFormatter(logging.Formatter):
       def format(self, record):
           return json.dumps({
               "timestamp": self.formatTime(record),
               "level": record.levelname,
               "message": record.getMessage(),
               "module": record.module
           })
   ```

2. **Error Tracking (Sentry)**
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.fastapi import FastApiIntegration
   
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[FastApiIntegration()],
       environment="production"
   )
   ```

3. **Metrics (Prometheus)**
   ```python
   from prometheus_client import Counter, Histogram
   
   request_count = Counter('requests_total', 'Total requests')
   request_duration = Histogram('request_duration_seconds', 'Request duration')
   ```

### Performance Optimization

1. **Database**
   - Connection pooling: `pool_size=20, max_overflow=40`
   - Query optimization with indexes
   - Caching with Redis

2. **Backend**
   - Gunicorn workers: `workers = 4 * cpu_count + 2`
   - Enable gzip compression
   - Cache endpoints with ETag

3. **Frontend**
   - Next.js static generation
   - Image optimization
   - Code splitting
   - CDN distribution

---

## Maintenance

### Regular Tasks

**Weekly**:
- Monitor error logs
- Check API response times
- Verify data integrity

**Monthly**:
- Database maintenance
- Review and update dependencies
- Test backup/restore process

**Quarterly**:
- Security audit
- Performance analysis
- Model evaluation and retraining

### Updates & Patching

```bash
# Backend
pip list --outdated
pip install --upgrade package_name

# Frontend
npm outdated
npm update

# Database
pg_dump traffic_twin_ai > backup.sql
# Apply migrations
psql traffic_twin_ai < migrations.sql
```

### Model Retraining

```bash
# Monthly or when data volume increases significantly
python train_model.py --data-path new_data.csv

# Rebuild FAISS index quarterly
python build_rag_index.py --data-path complete_data.csv
```

### Backup Strategy

```bash
# Daily automated backup (PostgreSQL)
pg_dump -h localhost -U postgres traffic_twin_ai | \
  gzip > backups/traffic_twin_ai_$(date +%Y%m%d).sql.gz

# Model artifacts backup
tar -czf backups/models_$(date +%Y%m%d).tar.gz backend/models/
```

---

## Scaling Considerations

### Current (Single Instance)
- Suitable for ~100 concurrent users
- Handles ~1000 incidents/day
- Response time: 200-500ms

### Scaled (Production)
- Load balancer + multiple instances
- Dedicated database server
- Redis cache layer
- CDN for static assets
- Async job queue (Celery)
- Managed vector database

### Autoscaling (Cloud)
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: traffic-twin-backend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: traffic-twin-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Troubleshooting

### Backend Issues

**Port already in use**:
```bash
# Linux/macOS
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Model not found**:
```bash
# Train model
python train_model.py --data-path data.csv
python build_rag_index.py --data-path data.csv
```

**Database connection failed**:
```bash
# Check PostgreSQL
psql -U postgres -h localhost -d traffic_twin_ai
# Verify DATABASE_URL in .env
```

### Frontend Issues

**API unreachable**:
- Check NEXT_PUBLIC_API_URL
- Verify backend is running
- Check CORS configuration

**Build fails**:
```bash
rm -rf .next node_modules
npm install
npm run build
```

---

## Rollback Procedures

```bash
# Backend
git revert <commit-hash>
git push origin main
# Re-deploy

# Frontend
vercel rollback

# Database
# From backup (if needed)
dropdb traffic_twin_ai
createdb traffic_twin_ai
psql traffic_twin_ai < backup.sql
```

---

**Last Updated**: 2024-01-15
