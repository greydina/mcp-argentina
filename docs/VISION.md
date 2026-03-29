# MCP Argentina — Vision Document

## Executive Summary

MCP Argentina es un servidor Model Context Protocol que provee datos económicos argentinos en tiempo real para LLMs y agentes de IA. El objetivo es ser **la referencia estándar** para cualquier agente que necesite entender la economía argentina.

## Current State (v0.1.0)

### What We Have
- ✅ Cotizaciones dólar (7 tipos)
- ✅ Históricos (30+ días)
- ✅ Inflación (INDEC)
- ✅ Riesgo país
- ✅ Monedas extranjeras (10+)
- ✅ Conversiones
- ✅ Gráficos ASCII
- ✅ Alertas (configurables)
- ✅ 85% test coverage
- ✅ Type-safe (mypy 0 errors)

### What's Missing
- ❌ Publicación PyPI
- ❌ Publicación ClawHub
- ❌ WebSocket real-time
- ❌ Persistencia de cache
- ❌ Observabilidad
- ❌ Rate limiting
- ❌ Retry logic

## Vision

### Short-Term (1 month)

**Goal: Production-Ready Release**

1. **Publicar en PyPI**
   - `pip install mcp-argentina`
   - Versioning semántico
   - GitHub releases con changelog

2. **Publicar en ClawHub**
   - Skill para OpenClaw
   - One-click install
   - Documentation en español

3. **Robustez**
   - Retry con backoff exponencial
   - Circuit breaker pattern
   - Rate limiting (token bucket)
   - Graceful degradation

### Medium-Term (3 months)

**Goal: Enterprise-Ready**

1. **Real-Time Updates**
   - WebSocket transport
   - Push notifications de cambios
   - Subscripciones por tipo

2. **Observabilidad**
   - OpenTelemetry traces
   - Prometheus metrics
   - Structured logging (JSON)
   - Health checks `/health`

3. **Persistencia**
   - Redis cache backend
   - SQLite para históricos largos
   - Warm cache on startup

4. **Nuevos Datos**
   - Tasas de interés (BCRA)
   - Bonos y acciones (BYMA)
   - Commodities (soja, trigo)
   - Reservas internacionales

### Long-Term (6-12 months)

**Goal: Ecosystem Leadership**

1. **API Gateway**
   - REST API pública
   - GraphQL endpoint
   - API keys y throttling
   - Dashboard de uso

2. **Multi-Country**
   - MCP LatAm (Brasil, Chile, Uruguay, México)
   - Arquitectura pluggable por país
   - Comparaciones regionales

3. **Analytics**
   - Predicciones (ML)
   - Análisis de sentimiento (noticias)
   - Correlaciones automáticas
   - Alertas inteligentes

4. **Integraciones**
   - Slack/Discord bots
   - Telegram bot
   - Notion integration
   - Google Sheets add-on

## Technical Strategy

### Architecture Evolution

```
v0.1 (current)     v0.2 (short-term)     v1.0 (long-term)
┌─────────────┐    ┌─────────────────┐    ┌───────────────────┐
│   MCP       │    │   MCP + REST    │    │   MCP + REST +    │
│   Server    │    │   + WebSocket   │    │   GraphQL + ML    │
└──────┬──────┘    └────────┬────────┘    └─────────┬─────────┘
       │                    │                       │
┌──────┴──────┐    ┌────────┴────────┐    ┌─────────┴─────────┐
│  Adapters   │    │    Adapters +   │    │   Adapters +      │
│  (HTTP)     │    │    Redis Cache  │    │   TimescaleDB     │
└─────────────┘    └─────────────────┘    └───────────────────┘
```

### Data Sources Roadmap

| Source | Data | Status | ETA |
|--------|------|--------|-----|
| dolarapi.com | Cotizaciones | ✅ Done | - |
| argentinadatos.com | Históricos, Inflación | ✅ Done | - |
| BCRA API | Tasas, Reservas | ⏳ Planned | Q2 |
| BYMA API | Bonos, Acciones | ⏳ Planned | Q2 |
| Ámbito Financiero | Noticias | ⏳ Planned | Q3 |

## Success Metrics

### Adoption
- 100+ PyPI downloads/month (month 1)
- 10+ ClawHub installs (month 2)
- 5+ GitHub stars (month 3)

### Quality
- 90%+ test coverage
- <1% error rate
- <500ms p99 latency

### Community
- 3+ contributors
- 10+ issues/PRs
- Spanish + English docs

## Non-Goals

Things we explicitly won't do:

1. **Trading/Investment Advice** — Solo datos, no recomendaciones
2. **Historical Data Storage** — Solo cache, no DB de históricos largos
3. **Custom Data Sources** — No APIs personalizadas por usuario
4. **Paid Tiers** — Open source, gratuito siempre

## Dependencies & Risks

### External Dependencies
- `dolarapi.com` — Puede caer o cambiar API
- `argentinadatos.com` — Puede cambiar estructura
- MCP SDK — Breaking changes posibles

### Mitigations
- Múltiples fuentes de datos (fallback)
- Tests de integración regulares
- Versioning estricto de SDK

## Contributors

Currently solo project. Looking for:
- Python developers
- Economic data experts
- Spanish/English translators
- DevOps for CI/CD

## Links

- **Repository**: https://github.com/greydina/mcp-argentina
- **Issues**: https://github.com/greydina/mcp-argentina/issues
- **Docs**: (coming soon)

---

_Last updated: 2026-03-29_
_Version: 0.1.0_
