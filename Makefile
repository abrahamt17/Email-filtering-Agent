.help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Run development server"
	@echo "  make prod          - Run production server"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make db-migrate    - Create database migration"
	@echo "  make db-upgrade    - Apply migrations"
	@echo "  make db-downgrade  - Rollback migrations"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View Docker logs"
	@echo "  make clean         - Clean up cache and artifacts"

.PHONY: help install dev prod test lint format db-migrate db-upgrade db-downgrade docker-build docker-up docker-down docker-logs clean

help: .help

install:
	pip install -r requirements.txt

dev:
	bash run_dev.sh

prod:
	bash run_prod.sh

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html

lint:
	flake8 app/
	pylint app/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

db-migrate:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

docker-build:
	docker build -t email-api:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	find . -type d -name '.coverage' -delete
	find . -type d -name 'htmlcov' -delete
	find . -type d -name 'dist' -delete
	find . -type d -name 'build' -delete
	find . -type d -name '*.egg-info' -delete
