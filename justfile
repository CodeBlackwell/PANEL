# ArchitX - Development Commands
set shell := ["bash", "-uc"]

# Run both backend and frontend (default)
dev:
    just backend & just frontend & wait

# Backend server
backend:
    cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Frontend server
frontend:
    cd frontend && npm run dev

# First-time setup
setup: setup-backend setup-frontend
    @echo "✓ Setup complete! Add your OPENAI_API_KEY to backend/.env"

setup-backend:
    cd backend && python -m venv venv
    cd backend && source venv/bin/activate && pip install -r requirements.txt
    cd backend && cp -n .env.example .env || true

setup-frontend:
    cd frontend && npm install

# Run all tests
test: test-backend test-frontend

test-backend:
    cd backend && source venv/bin/activate && pytest

test-frontend:
    cd frontend && npm run test

# Production build
build:
    cd frontend && npm run build

# Clean generated files
clean:
    rm -rf backend/venv backend/__pycache__ backend/.pytest_cache
    rm -rf frontend/node_modules frontend/dist

# Show available recipes
help:
    @just --list
