.PHONY: help install dev lint typecheck test test-unit test-integration build clean seed-canasta

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all deps (Python + Node)
	uv sync
	pnpm install

dev: ## Start all services locally
	docker compose -f infra/docker/compose/docker-compose.dev.yml up -d
	@echo "Postgres + Redis ready. Run 'make dev-api' and 'make dev-workers' separately."

dev-api: ## Start FastAPI dev server
	uv run --package cuantocuestave-api uvicorn cuantocuestave_api.main:app --reload --port 8000

dev-workers: ## Start Dramatiq workers
	uv run --package cuantocuestave-workers dramatiq cuantocuestave_workers.broker

dev-web: ## Start Astro dev server
	pnpm --filter web dev

dev-admin: ## Start Vite admin dev server
	pnpm --filter admin dev

lint: ## Lint Python + TS
	uv run ruff check .
	pnpm -r lint

format: ## Format Python + TS
	uv run ruff format .
	pnpm -r format

typecheck: ## Type-check Python + TS
	uv run mypy packages/ apps/api apps/workers
	pnpm -r typecheck

test: ## Run all tests
	uv run pytest

test-unit: ## Run unit tests only
	uv run pytest packages/ -k "not integration"

test-integration: ## Run integration tests (needs DB + Redis)
	uv run pytest -m integration

migrate: ## Run Alembic migrations
	uv run --package cuantocuestave-infrastructure alembic -c packages/infrastructure/alembic.ini upgrade head

migrate-new: ## New migration: make migrate-new MSG="description"
	uv run --package cuantocuestave-infrastructure alembic -c packages/infrastructure/alembic.ini revision --autogenerate -m "$(MSG)"

seed-canasta: ## Seed canasta básica products from data/canasta_basica_seed.yaml
	uv run python scripts/seed_canasta.py

build-web: ## Build Astro static site
	pnpm --filter web build

build-admin: ## Build Vite admin SPA
	pnpm --filter admin build

clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf apps/web/dist apps/web/.astro apps/admin/dist

infra-up: ## Start observability stack
	docker compose -f infra/docker/compose/docker-compose.observability.yml up -d

infra-down: ## Stop all docker services
	docker compose -f infra/docker/compose/docker-compose.dev.yml down
	docker compose -f infra/docker/compose/docker-compose.observability.yml down
