# ADR 0004 — pgvector dentro de Neon vs vector DB externa

**Status**: Accepted  
**Date**: 2026-04-27

## Context
Matching de productos requiere búsqueda de vecinos cercanos sobre ~1000-5000 embeddings (384 dims). Opciones: pgvector (Neon ya lo soporta), Qdrant, Weaviate.

## Decision
pgvector dentro de Neon. Índice ivfflat con `lists = sqrt(N)`. Una sola base de datos, sin contenedor extra, sin backup extra.

## Consequences
✅ Zero additional infrastructure. Neon ya está provisionado con pgvector.  
✅ Joins con tablas de precios y listings nativos.  
✅ Queries < 10ms para N < 10k con ivfflat.  
⚠️ Si el corpus crece a >100k listings necesitamos HNSW index o migrar a Qdrant. Evaluamos en Fase 4+.
