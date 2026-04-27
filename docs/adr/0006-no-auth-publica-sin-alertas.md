# ADR 0006 — Sin auth pública, sin alertas email en MVP

**Status**: Accepted  
**Date**: 2026-04-27

## Context
Inicialmente planeamos alertas por email con auth de usuario. Reconsideramos el scope para simplificar MVP.

## Decision
Sitio público completamente read-only. Sin alertas email, sin tabla users/alerts, sin Resend. Anomalías y forecasts se muestran como badges públicos en las páginas de producto.

## Consequences
✅ Elimina: Resend, tabla users, tabla alerts, reset flow, privacy policy, unsubscribe flow.  
✅ Ahorra 1 semana del roadmap (Fase 5 original).  
✅ Superficie de ataque reducida.  
⚠️ Sin alertas → usuarios deben revisar manualmente. Decisión reversible: alertas pueden agregarse post-MVP sin cambiar arquitectura core.
