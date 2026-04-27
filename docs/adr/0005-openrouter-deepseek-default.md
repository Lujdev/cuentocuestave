# ADR 0005 — OpenRouter con deepseek/deepseek-v4-flash como LLM default

**Status**: Accepted  
**Date**: 2026-04-27

## Context
Matching de listings requiere LLM para casos ambiguos (cosine sim 0.55-0.92). Necesitamos: bajo costo, JSON structured output, multilingual (español venezolano), alta disponibilidad.

## Decision
OpenRouter como gateway (API compatible con openai SDK). Default: `deepseek/deepseek-v4-flash` ($0.14/$0.28 por 1M tokens). Fallback: `anthropic/claude-haiku-4.5` cuando confidence < 0.7.

## Consequences
✅ ~25-30x más barato que Claude Haiku solo → cap $1/mes en MVP.  
✅ Sin vendor lock-in: cambio de modelo = cambio de env var.  
✅ A/B real DeepSeek vs Haiku sobre ground truth = material de portafolio.  
✅ Cache por prompt hash en Redis (90d TTL) reduce costos adicionales.  
⚠️ Latencia OpenRouter puede ser variable (extra hop). Mitigado con timeout 10s y fallback.
