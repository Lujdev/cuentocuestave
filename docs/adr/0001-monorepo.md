# ADR 0001 — Monorepo con uv workspaces + pnpm workspaces

**Status**: Accepted  
**Date**: 2026-04-27

## Context
Proyecto con 4 paquetes Python y 2 apps Node. Necesitamos compartir código (domain entre api y workers), versionar juntos y simplificar CI.

## Decision
Monorepo único: `uv workspaces` para Python, `pnpm workspaces` para TS. Una sola raíz de repositorio.

## Consequences
✅ Cambios cross-package atómicos en un solo commit.  
✅ CI unificado.  
✅ uv resuelve dependencias internas sin publicar a PyPI.  
⚠️ Build de Docker copia contexto completo — mitigado con `.dockerignore`.
