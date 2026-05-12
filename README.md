# AI Email Processing System

A production-ready FastAPI application for processing emails with AI analysis.

## Features

- **Modular Architecture**: Separated concerns with api, services, models, and utils folders
- **Async/Await**: Full async support with SQLAlchemy and asyncpg
- **PostgreSQL Integration**: Production-grade database with connection pooling
- **Environment Configuration**: 12-factor app configuration with pydantic-settings
- **Structured Logging**: File and console logging with rotation
- **API Documentation**: Interactive Swagger UI and ReDoc documentation
- **Health Checks**: Liveness and readiness probes for Kubernetes
- **Docker Ready**: Dockerfile and docker-compose for containerization
- **Scalable Design**: Ready for horizontal scaling with proper database pooling

## Project Structure

```
├── app/
│   ├── api/                 # API route handlers
│   │   ├── email_routes.py
│   │   ├── health_routes.py
│   │   └── __init__.py
│   ├── core/                # Core configuration
│   │   ├── config.py        # Environment and settings
│   │   ├── database.py      # Database connection setup
│   │   ├── logging.py       # Logging configuration
│   │   └── __init__.py
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── models.py        # Database models
│   │   └── __init__.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── email.py
│   │   └── __init__.py
│   ├── services/            # Business logic
│   │   ├── email_service.py
│   │   └── __init__.py
│   ├── utils/               # Utility functions
│   │   ├── security.py      # Security utilities
│   │   └── __init__.py
│   ├── main.py              # FastAPI app factory
│   └── __init__.py
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
├── Dockerfile               # Container image
├── docker-compose.yml       # Docker compose configuration
├── pyproject.toml           # Python project configuration
├── requirements.txt         # Python dependencies
├── conftest.py              # Pytest configuration
├── run_dev.sh               # Development server script
├── run_prod.sh              # Production server script
└── README.md                # This file
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone the repository**
   ```bash
   cd "AI email int sys"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Run development server**
   ```bash
   bash run_dev.sh
   ```

Server will be available at http://localhost:8000

## Docker Setup

### Using Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- FastAPI application

Access the application at http://localhost:8000

## API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI analysis
- `SECRET_KEY`: Secret key for JWT tokens
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENVIRONMENT`: Environment (development, staging, production)

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Running Tests

```bash
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --cov=app               # With coverage report
pytest -k email                 # Run specific test
pytest -m asyncio              # Run async tests
```

## Development

### Code Quality Tools

Format code:
```bash
black app/
```

Sort imports:
```bash
isort app/
```

Lint code:
```bash
flake8 app/
pylint app/
```

Type checking:
```bash
mypy app/
```

All at once:
```bash
black app/ && isort app/ && flake8 app/ && mypy app/
```

## Production Deployment

### Build and Push Docker Image

```bash
docker build -t email-api:latest .
docker tag email-api:latest registry.example.com/email-api:latest
docker push registry.example.com/email-api:latest
```

### Kubernetes Deployment

Example deployment configuration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: email-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: email-api
  template:
    metadata:
      labels:
        app: email-api
    spec:
      containers:
      - name: email-api
        image: registry.example.com/email-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: email-api-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: email-api-secrets
              key: openai-api-key
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

## Scaling Considerations

1. **Database Connection Pooling**: Configured with `DB_POOL_SIZE` and `DB_MAX_OVERFLOW`
2. **Redis Caching**: Optional caching layer for performance
3. **Async Operations**: Full async support for high concurrency
4. **Worker Count**: Set `WORKERS` based on CPU cores (2 * cores + 1)
5. **Load Balancing**: Deploy multiple instances behind a load balancer
6. **Monitoring**: Use health check endpoints for orchestration

## API Endpoints

### Health Check
- `GET /api/v1/health` - Application health status

### Emails
- `POST /api/v1/emails` - Create new email
- `GET /api/v1/emails` - List emails with pagination
- `GET /api/v1/emails/{email_id}` - Get email details
- `PATCH /api/v1/emails/{email_id}` - Update email
- `DELETE /api/v1/emails/{email_id}` - Delete email
- `POST /api/v1/emails/{email_id}/process` - Process with AI

## Logging

Logs are written to:
- **Console**: Always enabled
- **File**: `logs/app.log` (rotated daily, max 10 files)

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Security

- CORS enabled for frontend communication
- JWT token authentication ready
- Password hashing with bcrypt
- SQL injection protection with parameterized queries
- HTTPS ready (configure with reverse proxy)

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -h localhost -U email_user -d email_processing_db
```

### Port Already in Use
```bash
# Change port in environment or
lsof -i :8000
kill -9 <PID>
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT

## Support

For issues and questions, please create a GitHub issue.
