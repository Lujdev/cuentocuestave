# ADR 0003 — Scrapling 0.4.7 como capa de scraping

**Status**: Accepted  
**Date**: 2026-04-27

## Context
Supermercados venezolanos online usan SPAs con Cloudflare/antibot. Necesitamos TLS fingerprinting, adaptive selectors y compatibilidad con Playwright.

## Decision
Scrapling 0.4.7 (pin exacto). Wrappea Playwright + curl_cffi + browserforge. `ScraperPort` en domain permite swap sin tocar lógica de negocio.

## Consequences
✅ Adaptive selectors mitigan DOM cambiantes silenciosamente.  
✅ Cloudflare bypass built-in.  
✅ Una sola lib en lugar de httpx + selectolax + playwright + playwright-stealth.  
⚠️ Pre-1.0 → breaking changes posibles. Mitigado con pin exacto y Renovate con review manual.  
⚠️ Si Scrapling abandona el proyecto → swap a Playwright puro vía ScraperPort sin tocar domain/application.
