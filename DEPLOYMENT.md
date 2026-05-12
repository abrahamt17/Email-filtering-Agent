# Deployment & Scaling Guide

## Production Deployment

### Prerequisites
- Docker & Docker Compose or Kubernetes cluster
- PostgreSQL database (managed or self-hosted)
- Redis (optional, for caching)
- Container registry

### Environment Setup

1. **Create production environment file**
```bash
cp .env.example .env.production
# Edit with production values:
# - Strong SECRET_KEY
# - Production DATABASE_URL
# - Real OPENAI_API_KEY
# - Set ENVIRONMENT=production
# - Set DEBUG=false
```

2. **Database Setup**
```bash
# Run migrations
docker run --rm -e DATABASE_URL="postgresql://..." app:latest alembic upgrade head
```

### Docker Deployment

#### Build Image
```bash
docker build -t email-api:1.0.0 .
docker tag email-api:1.0.0 registry.example.com/email-api:1.0.0
docker push registry.example.com/email-api:1.0.0
```

#### Single Server (Docker Compose)
```bash
docker-compose -f docker-compose.yml up -d
```

### Kubernetes Deployment

#### Prerequisites
- kubectl configured
- Helm (optional)
- Ingress controller (nginx-ingress, traefik, etc.)

#### Basic Deployment

1. **Create namespace**
```bash
kubectl create namespace email-api
```

2. **Create secrets**
```bash
kubectl create secret generic email-api-secrets \
  --from-literal=database-url=postgresql+asyncpg://user:pass@host/db \
  --from-literal=openai-api-key=sk-... \
  --from-literal=secret-key=your-secret-key \
  -n email-api
```

3. **Deploy application**
```bash
kubectl apply -f k8s/deployment.yaml -n email-api
kubectl apply -f k8s/service.yaml -n email-api
kubectl apply -f k8s/ingress.yaml -n email-api
```

#### Scaling
```bash
# Horizontal scaling
kubectl scale deployment email-api --replicas=3 -n email-api

# Auto-scaling (requires metrics-server)
kubectl apply -f k8s/hpa.yaml -n email-api
```

### Load Balancing

#### Nginx Configuration
```nginx
upstream email_api {
    least_conn;
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://email_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running operations
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /api/v1/health {
        access_log off;
        proxy_pass http://email_api;
    }
}
```

## Performance Optimization

### Database Connection Pooling
```python
# In config.py
DB_POOL_SIZE = 20          # Connections to maintain
DB_MAX_OVERFLOW = 10       # Extra connections allowed
DB_POOL_PRE_PING = True    # Verify connections before use
```

**Scaling Formula**: `POOL_SIZE = (num_workers * 2) + spare_connections`

### Worker Configuration
```bash
# For 4 CPU cores
WORKERS = (4 * 2) + 1 = 9

# Run with
gunicorn app.main:app --workers 9 --worker-class uvicorn.workers.UvicornWorker
```

### Redis Caching
```python
# Enable in .env
REDIS_ENABLED=true
REDIS_URL=redis://redis:6379/0
```

Cache email processing results to reduce database queries:
```python
# In email_service.py
async def get_email_cached(email_id: int):
    cache_key = f"email:{email_id}"
    # Check cache first
    # Hit: return cached result
    # Miss: query database and cache result
```

## Monitoring & Observability

### Health Checks
```bash
# Liveness probe - is app running?
curl http://localhost:8000/api/v1/health

# Check response
{
    "status": "ok",
    "version": "1.0.0",
    "environment": "production",
    "database": true,
    "timestamp": "2024-01-01T00:00:00"
}
```

### Logging

**File Rotation**
```python
# logs/app.log - rotated daily
# Retention: 5 backup files × 10MB each = 50MB
```

**Log Levels in Production**
- Critical errors: CRITICAL, ERROR
- Warnings: WARNING
- Information: INFO
- Debug: DEBUG (disabled in production)

### Metrics

Add Prometheus metrics:
```python
# In app/core/metrics.py
from prometheus_client import Counter, Histogram

email_processed = Counter(
    'emails_processed_total',
    'Total emails processed',
    ['status']
)

processing_duration = Histogram(
    'email_processing_seconds',
    'Email processing duration'
)
```

### Error Tracking

Integrate Sentry:
```python
# In main.py
import sentry_sdk

sentry_sdk.init(
    dsn="https://key@sentry.io/project",
    environment="production",
    traces_sample_rate=0.1
)
```

## Backup & Recovery

### Database Backup
```bash
# Daily backups
pg_dump -U email_user email_processing_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Automated with pg_basebackup
pg_basebackup -h localhost -D /backups -U replication -v -P
```

### Point-in-Time Recovery
```bash
# Restore from backup
psql -U email_user email_processing_db < backup_20240101.sql
```

## Security Hardening

### API Security
- Enable HTTPS/TLS (configure reverse proxy)
- Use API keys/JWT for authentication
- Rate limiting: `pip install slowapi`
- CORS: Already configured in main.py

### Database Security
- Use strong passwords
- Enable SSL connections
- Run in private network/VPC
- Regular security updates

### Container Security
- Use non-root user (already configured in Dockerfile)
- Scan for vulnerabilities: `docker scan email-api:latest`
- Keep base image updated: `python:3.11-slim`

## Cost Optimization

### AWS Deployment Example
```yaml
RDS PostgreSQL:
  - Instance: db.t3.medium ($0.058/hour)
  - Storage: 100GB gp3 ($0.11/GB/month)
  - Backup: 7 days retention
  
EC2 Instances:
  - Type: t3.medium (1 vCPU, 4GB RAM)
  - Quantity: 3 instances × $0.0396/hour
  - Load Balancer: ALB $16/month + data charges

Estimated Monthly Cost: $500-800
```

### Cost Reduction Strategies
- Use Fargate for variable workloads
- Reserved instances for predictable load
- Auto-scaling based on metrics
- Database connection pooling
- Redis caching for frequent queries

## Disaster Recovery

### Failover Strategy
1. Multi-region database replication
2. DNS failover (Route53, Cloudflare)
3. RTO (Recovery Time Objective): 5 minutes
4. RPO (Recovery Point Objective): 1 minute

### Backup Schedule
```bash
# Full backup daily at 2 AM
0 2 * * * pg_dump -U email_user email_processing_db | gzip > /backups/full_$(date +\%Y\%m\%d).sql.gz

# Incremental backups every 6 hours
0 */6 * * * pg_dump -U email_user --incremental email_processing_db | gzip > /backups/incr_$(date +\%Y\%m\%d_%H).sql.gz
```

## Checklist Before Production

- [ ] Database backups tested and working
- [ ] SSL/TLS certificates configured
- [ ] Environment variables set correctly
- [ ] Health checks passing
- [ ] Monitoring and alerting configured
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Logging aggregation setup
- [ ] Disaster recovery plan documented
- [ ] Team trained on deployment procedures
- [ ] Runbook created for common issues
- [ ] Incident response plan in place
