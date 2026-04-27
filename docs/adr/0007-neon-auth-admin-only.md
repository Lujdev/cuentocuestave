# ADR 0007 — Neon Auth (Stack Auth) solo para admin dashboard

**Status**: Accepted  
**Date**: 2026-04-27

## Context
Necesitamos proteger `/api/admin/*` y el SPA admin para un solo usuario (luisjmolina29@gmail.com). Opciones: password propio, magic link propio, Neon Auth.

## Decision
Neon Auth (Stack Auth integrado con neon_auth schema). Magic link únicamente. Email allowlist de 1 usuario validado en el middleware FastAPI via JWKS verify del JWT de Stack Auth.

## Consequences
✅ Sin gestión de passwords, sin reset flow.  
✅ neon_auth schema ya provisionado en la DB (verificado vía MCP).  
✅ Componentes React @stackframe/react en admin SPA.  
⚠️ Vendor coupling con Neon Auth. Si migramos DB de Neon, la auth se separa. Mitigado porque el plan es quedarse en Neon largo plazo.
