# ADR 0002 — Frontend split: Astro 5 público + Vite+React admin

**Status**: Accepted  
**Date**: 2026-04-27

## Context
Sitio público es read-only (precios, histórico, analytics). Admin es autenticado, un solo usuario, sin SEO.

## Decision
- `apps/web`: Astro 5 SSG. HTML pre-renderizado. Cero Node runtime. SEO máximo.
- `apps/admin`: Vite + React SPA. Sin SEO necesario. Neon Auth.

## Consequences
✅ Cero Node runtime para sitio público → menos RAM en VPS.  
✅ Lighthouse SEO >95 sin esfuerzo.  
✅ SPA admin simple de mantener para un solo usuario.  
⚠️ Dos apps separadas → dos builds, dos contenedores nginx. Complejidad manejable.
