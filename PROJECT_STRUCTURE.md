# Project Structure Summary

## Complete Directory Tree

```
AI email int sys/
│
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application factory
│   │
│   ├── api/                      # API routes and endpoints
│   │   ├── __init__.py
│   │   ├── email_routes.py       # Email CRUD and processing endpoints
│   │   └── health_routes.py      # Health check endpoints
│   │
│   ├── core/                     # Core configuration and setup
│   │   ├── __init__.py
│   │   ├── config.py             # Environment configuration (12-factor)
│   │   ├── database.py           # SQLAlchemy async setup
│   │   └── logging.py            # Logging configuration
│   │
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   └── models.py             # Database models (Email, User, ProcessingLog)
│   │
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   └── email.py              # Email schemas and validation
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   └── email_service.py      # Email processing service
│   │
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── security.py           # Authentication, hashing, JWT
│
├── alembic/                       # Database migrations
│   ├── env.py                    # Alembic environment configuration
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Migration scripts
│
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_email_service.py     # Email service unit tests
│
├── k8s/                          # Kubernetes manifests
│   └── deployment.yaml           # K8s deployment, service, HPA
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions CI/CD pipeline
│
├── logs/                         # Application logs (created at runtime)
│   ├── app.log
│   ├── access.log
│   └── error.log
│
# Configuration and Setup Files
├── .env.example                  # Example environment variables
├── .gitignore                    # Git ignore patterns
├── alembic.ini                   # Alembic configuration
├── conftest.py                   # Pytest configuration
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Multi-container setup
├── Makefile                      # Development commands
├── pyproject.toml                # Python project configuration (black, isort, mypy, etc.)
├── requirements.txt              # Python dependencies
├── run_dev.sh                    # Development server script
├── run_prod.sh                   # Production server script
│
# Documentation
├── README.md                     # Project overview and setup
├── DEPLOYMENT.md                 # Production deployment guide
└── PROJECT_STRUCTURE.md          # This file
```

## File Descriptions

### Application Core

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application factory with middleware, routes, and lifecycle management |
| `app/core/config.py` | Pydantic settings for 12-factor app configuration |
| `app/core/database.py` | SQLAlchemy async engine, session management, and DatabaseManager |
| `app/core/logging.py` | Structured logging with file rotation and console output |

### API Layer

| File | Purpose |
|------|---------|
| `app/api/email_routes.py` | REST endpoints for email CRUD and AI processing |
| `app/api/health_routes.py` | Health check and system status endpoints |

### Data Layer

| File | Purpose |
|------|---------|
| `app/models/models.py` | SQLAlchemy ORM models (Email, User, ProcessingLog) |
| `app/schemas/email.py` | Pydantic validation schemas for requests/responses |

### Business Logic

| File | Purpose |
|------|---------|
| `app/services/email_service.py` | Email processing service with CRUD operations |

### Utilities

| File | Purpose |
|------|---------|
| `app/utils/security.py` | Password hashing, JWT tokens, pagination helpers |

### Configuration & Deployment

| File | Purpose |
|------|---------|
| `.env.example` | Template for environment variables |
| `Dockerfile` | Production-ready Docker image with non-root user |
| `docker-compose.yml` | PostgreSQL, Redis, and app containers |
| `pyproject.toml` | Tool configurations (black, isort, mypy, pytest, ruff) |
| `requirements.txt` | Python dependencies (42 packages) |
| `Makefile` | Development shortcuts (make dev, make test, etc.) |

### Development & Testing

| File | Purpose |
|------|---------|
| `conftest.py` | Pytest configuration and fixtures |
| `tests/test_email_service.py` | Unit tests for email service |

### Database

| File | Purpose |
|------|---------|
| `alembic.ini` | Alembic migration configuration |
| `alembic/env.py` | Migration environment setup |
| `alembic/script.py.mako` | Migration template |

### Deployment

| File | Purpose |
|------|---------|
| `k8s/deployment.yaml` | Kubernetes Deployment, Service, and HPA |
| `.github/workflows/ci-cd.yml` | GitHub Actions pipeline |
| `run_dev.sh` | Development server startup |
| `run_prod.sh` | Production server startup (gunicorn) |

## Key Features

### ✅ Production-Ready Architecture
- **Modular design**: Separated concerns (api, services, models, utils)
- **Async/Await**: Full async support with SQLAlchemy and asyncpg
- **Connection pooling**: Configured for high-concurrency scenarios
- **Error handling**: Global exception handlers with proper HTTP status codes

### ✅ Database
- **PostgreSQL**: With asyncpg for async operations
- **SQLAlchemy ORM**: Declarative models with relationships
- **Migrations**: Alembic for version-controlled schema changes
- **Indexes**: Optimized queries with strategic database indexes

### ✅ Configuration
- **12-Factor App**: Environment variable based configuration
- **Pydantic Settings**: Type-safe configuration with validation
- **Multiple Environments**: Development, staging, production support

### ✅ API Documentation
- **Swagger UI**: Interactive API documentation at `/docs`
- **ReDoc**: Alternative API documentation at `/redoc`
- **OpenAPI Schema**: Machine-readable API definition

### ✅ Logging & Monitoring
- **Structured Logging**: File and console output
- **Log Rotation**: Automatic cleanup of old logs
- **Health Checks**: Liveness and readiness probes
- **Metrics Ready**: Structure for Prometheus integration

### ✅ Security
- **Password Hashing**: bcrypt for secure password storage
- **JWT Authentication**: Token generation and validation ready
- **CORS**: Configurable cross-origin resource sharing
- **Non-root Container**: Docker image runs as non-root user

### ✅ Testing
- **Unit Tests**: pytest with asyncio support
- **Test Configuration**: Database fixtures and test settings
- **Coverage**: Coverage reporting capabilities

### ✅ Containerization
- **Docker**: Production-ready Dockerfile with multi-stage builds
- **Docker Compose**: Complete stack (PostgreSQL, Redis, App)
- **Health Checks**: Container health monitoring

### ✅ Scalability
- **Horizontal Scaling**: Multiple workers and replicas
- **Load Balancing**: Ready for nginx, HAProxy, or cloud LB
- **Connection Pooling**: Database connection reuse
- **Kubernetes Ready**: Deployment manifests included

## Dependencies Overview

### Core Framework
- FastAPI: Web framework
- Uvicorn: ASGI server
- Pydantic: Data validation

### Database
- SQLAlchemy: ORM
- asyncpg: PostgreSQL async driver
- Alembic: Database migrations

### Security
- python-jose: JWT tokens
- passlib: Password hashing
- bcrypt: Cryptographic hashing

### Development
- pytest: Testing framework
- black: Code formatting
- mypy: Type checking
- ruff: Fast Python linter

### Production
- gunicorn: Production server
- python-multipart: Multipart forms
- python-dotenv: Environment variables

## API Endpoints

### Health
- `GET /api/v1/health` - Application health status

### Emails
- `POST /api/v1/emails` - Create email
- `GET /api/v1/emails` - List emails (paginated)
- `GET /api/v1/emails/{id}` - Get email details
- `PATCH /api/v1/emails/{id}` - Update email
- `DELETE /api/v1/emails/{id}` - Delete email
- `POST /api/v1/emails/{id}/process` - Process with AI

## Quick Start Commands

```bash
# Install dependencies
make install

# Run development server
make dev

# Run tests
make test

# Format code
make format

# Run linters
make lint

# Database migrations
make db-migrate "Add new column"
make db-upgrade
make db-downgrade

# Docker
make docker-build
make docker-up
make docker-down

# Production server
make prod
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENVIRONMENT` | development | App environment |
| `DEBUG` | false | Debug mode |
| `DATABASE_URL` | postgresql://... | Database connection |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection |
| `OPENAI_API_KEY` | None | AI API key |
| `SECRET_KEY` | Change in production | JWT secret |
| `LOG_LEVEL` | INFO | Logging level |
| `WORKERS` | 4 | Worker processes |

## Performance Tuning

### Database
- Connection pool size: 20 (configurable)
- Max overflow: 10 (temporary connections)
- Pool pre-ping: Enabled (connection validation)
- Recycle connections: Every 3600 seconds

### Application
- Worker count: 2 × CPU + 1
- Worker class: UvicornWorker
- Graceful timeout: 30 seconds
- Request timeout: 60 seconds

### Caching
- Redis support (optional)
- Configurable TTL
- Client-side caching headers

## Deployment Paths

### Local Development
```bash
bash run_dev.sh
```

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

### Traditional Server
```bash
bash run_prod.sh  # Gunicorn with 4 workers
```

## Next Steps

1. **Configure `.env`**: Copy `.env.example` to `.env` and update values
2. **Setup Database**: Run `make db-upgrade` to create tables
3. **Install Dependencies**: Run `make install`
4. **Run Server**: Run `make dev` for development
5. **Test API**: Visit http://localhost:8000/docs
6. **Read Docs**: See README.md and DEPLOYMENT.md

## Support & Scaling

- **Monitoring**: Integrate Prometheus/Grafana
- **Logging**: Use ELK stack or Splunk
- **Tracing**: Add Jaeger for distributed tracing
- **Alerts**: Configure PagerDuty or Opsgenie
- **CI/CD**: GitHub Actions pipeline included

---

This is a complete, production-ready FastAPI project structure suitable for scaling to handle millions of emails with AI processing.
