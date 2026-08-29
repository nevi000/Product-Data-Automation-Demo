.PHONY: help install backend frontend test lint build

help:
	@echo "install   - install backend + frontend deps"
	@echo "backend   - run the FastAPI dev server (:8000)"
	@echo "frontend  - run the Vite dev server (:5173)"
	@echo "test      - run backend tests"
	@echo "lint      - ruff + eslint"
	@echo "build     - production build of the frontend"

install:
	cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/pytest

lint:
	cd backend && .venv/bin/ruff check .
	cd frontend && npx eslint .

build:
	cd frontend && npm run build
