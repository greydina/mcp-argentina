# MCP Argentina - Visión del Producto

## Resumen Ejecutivo

**MCP Argentina** es un servidor Model Context Protocol (MCP) que provee acceso estructurado a datos económicos y financieros de Argentina en tiempo real.

Permite a agentes de IA (Claude, OpenClaw, Cursor, etc.) consultar cotizaciones, indicadores económicos y datos del BCRA mediante tools estandarizados.

---

## Objetivos

### Producto
- Primer MCP server dedicado a datos económicos de Argentina
- Production-ready desde día 1
- Open source (MIT license)
- Documentación 100% en español

### Técnicos
- Python 3.11+
- Clean Architecture (domain, application, infrastructure)
- Test coverage mínimo 85%
- Type hints completos (mypy strict)
- Async-first
- Zero external dependencies pagos

---

## Alcance MVP (v0.1.0)

### Tools (MCP)

| Tool | Descripción | Data Source |
|------|-------------|-------------|
| `get_dolar` | Cotización dólar (blue, oficial, MEP, CCL, cripto, tarjeta) | dolarapi.com |
| `get_inflacion` | Inflación mensual/anual/acumulada | BCRA / datos.gob.ar |
| `get_riesgo_pais` | Riesgo país actual e histórico | ambito.com / dolarapi |
| `get_cotizaciones` | Todas las cotizaciones en una llamada | dolarapi.com |
| `convertir` | Convertir ARS ↔ USD con tipo de cambio específico | calculated |

### Resources (MCP)

| Resource | Descripción |
|----------|-------------|
| `economia://cotizaciones/actual` | Snapshot actual de todas las cotizaciones |
| `economia://indicadores/resumen` | Resumen de indicadores clave |

### Prompts (MCP)

| Prompt | Descripción |
|--------|-------------|
| `analisis_economico` | Template para análisis de situación económica |
| `comparar_dolares` | Comparación entre tipos de cambio |

---

## Arquitectura

```
mcp_argentina/
├── domain/                 # Entidades y value objects
│   ├── entities/
│   │   ├── cotizacion.py
│   │   ├── indicador.py
│   │   └── moneda.py
│   └── value_objects/
│       ├── precio.py
│       └── fecha.py
├── application/            # Casos de uso
│   ├── use_cases/
│   │   ├── get_dolar.py
│   │   ├── get_inflacion.py
│   │   └── convertir.py
│   └── ports/              # Interfaces (abstracciones)
│       ├── cotizacion_repository.py
│       └── indicador_repository.py
├── infrastructure/         # Implementaciones concretas
│   ├── adapters/
│   │   ├── dolarapi_adapter.py
│   │   ├── bcra_adapter.py
│   │   └── cache_adapter.py
│   └── mcp/
│       ├── server.py       # MCP server principal
│       ├── tools.py        # Definición de tools
│       ├── resources.py    # Definición de resources
│       └── prompts.py      # Definición de prompts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                   # Documentación en español
│   ├── README.md
│   ├── instalacion.md
│   ├── uso.md
│   └── api.md
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## Stack Técnico

| Componente | Tecnología |
|------------|------------|
| Runtime | Python 3.11+ |
| MCP SDK | mcp (oficial) |
| HTTP Client | httpx (async) |
| Validation | pydantic v2 |
| Testing | pytest + pytest-asyncio + pytest-cov |
| Linting | ruff |
| Type Checking | mypy (strict) |
| Docs | mkdocs + mkdocs-material |
| CI/CD | GitHub Actions |

---

## Roadmap

### v0.1.0 (MVP)
- [ ] 5 tools básicos
- [ ] 2 resources
- [ ] 2 prompts
- [ ] Tests 85%+
- [ ] Docs español
- [ ] Publicar en GitHub

### v0.2.0
- [ ] Cache inteligente (TTL por tipo de dato)
- [ ] Históricos (últimos 30 días)
- [ ] Tool `get_tendencia` (análisis de tendencia)

### v0.3.0
- [ ] Integración BCRA API oficial
- [ ] Datos de inflación por rubro
- [ ] Alertas de variación

### v1.0.0
- [ ] Publicar en PyPI
- [ ] Publicar en ClawHub
- [ ] Docker image
- [ ] Helm chart (opcional)

---

## Criterios de Aceptación

### Funcionales
- [ ] Todos los tools responden en <2 segundos
- [ ] Datos actualizados (max 5 min delay)
- [ ] Manejo de errores graceful
- [ ] Retry automático en fallos de red

### No Funcionales
- [ ] Test coverage ≥85%
- [ ] Zero warnings en mypy strict
- [ ] Zero errors en ruff
- [ ] Documentación completa en español
- [ ] README con ejemplos de uso

---

## Data Sources

### Gratuitos (MVP)
- **dolarapi.com** — cotizaciones dólar, riesgo país
- **datos.gob.ar** — datos abiertos del gobierno

### Futuro (requieren auth)
- **BCRA API** — datos oficiales (gratis con registro)
- **estadisticasbcra.com** — wrapper BCRA (requiere token)

---

## Licencia

MIT License — uso comercial y personal permitido.

---

*Documento generado: 2026-03-28*
*Versión: 0.1.0-draft*
