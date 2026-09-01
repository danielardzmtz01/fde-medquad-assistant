.PHONY: help install test lint format dev-backend dev-frontend tf-dev-plan tf-dev-apply clean

help:
	@echo "Available commands:"
	@echo "  make install       Install all Python & Node dependencies"
	@echo "  make test          Run pytest suite with code coverage"
	@echo "  make lint          Run ruff linting on backend"
	@echo "  make format        Run ruff formatter"
	@echo "  make dev-backend   Start FastAPI development server"
	@echo "  make dev-frontend  Start Vite React frontend"
	@echo "  make tf-dev-plan   Run Terraform plan for dev environment"
	@echo "  make tf-dev-apply  Apply Terraform infrastructure for dev"

install:
	pip install -r src/backend/requirements.txt
	cd src/frontend && npm install

test:
	PYTHONPATH=src/backend pytest tests/ -v --cov=src/backend/app --cov-report=term-missing

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

dev-backend:
	uvicorn app.main:app --app-dir src/backend --reload --port 8080

dev-frontend:
	cd src/frontend && npm run dev

tf-dev-plan:
	cd terraform/environments/dev && terraform init && terraform plan

tf-dev-apply:
	cd terraform/environments/dev && terraform apply -auto-approve

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
