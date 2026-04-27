# cuantocuestave — Instrucciones para Claude

## Proyecto
Comparador público de precios de supermercados venezolanos. Stack: Python 3.12 + FastAPI + Scrapling + Neon PostgreSQL 18 + OpenRouter (DeepSeek Flash) + Astro 5 + Vite+React. Arquitectura hexagonal estricta. Monorepo uv + pnpm.

## Reglas de arquitectura
- `packages/domain` NUNCA importa infra ni application. Solo stdlib + pydantic.
- `packages/application` solo importa `domain`.
- `packages/infrastructure` implementa puertos de `domain`.
- `apps/api` y `apps/workers` solo cablean DI — no tienen lógica de negocio.

## Convenciones
- Nuevos scrapers: heredar de `BaseScrapler` en `packages/infrastructure/src/cuantocuestave_infra/scrapers/base.py`.
- Nuevos casos de uso: en `packages/application/src/cuantocuestave_application/use_cases/`.
- Nuevos actores Dramatiq: en `apps/workers/src/cuantocuestave_workers/actors/` y registrar en `scheduler.py`.
- Tests de integración marcar con `@pytest.mark.integration`.

## Fase actual: Fase 0 — Scaffolding
Ver plan completo en `~/.claude/plans/linear-nibbling-eagle.md`.

## Neon DB
- Project ID: `still-meadow-43534954`
- Region: aws-us-east-1
- PG: 18.2
- `neon_auth` schema provisionado (Stack Auth listo)
- Para migraciones: `make migrate-new MSG="descripcion"` y `make migrate`

## Comandos frecuentes
```
make install          # instalar todo
make dev              # levantar Postgres + Redis local
make dev-api          # FastAPI en modo desarrollo
make dev-workers      # Dramatiq workers
make dev-web          # Astro dev server
make lint             # ruff + eslint
make typecheck        # mypy + tsc
make test             # todos los tests
```
