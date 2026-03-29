# MCP Argentina 🇦🇷

Servidor Model Context Protocol (MCP) para datos económicos de Argentina en tiempo real.

## Features

- 💵 **Cotizaciones dólar**: Oficial, Blue, MEP, CCL, Tarjeta, Cripto, Mayorista
- 📈 **Históricos**: 30+ días de evolución de cotizaciones
- 📊 **Inflación**: Mensual, interanual y acumulada (INDEC)
- 🌡️ **Riesgo país**: Índice EMBI en tiempo real
- 💱 **Monedas**: EUR, BRL, UYU, CLP y 10+ monedas extranjeras
- 🔔 **Alertas**: Monitoreo de umbrales de precio
- 📉 **Gráficos**: Visualización ASCII de tendencias
- 🔄 **Conversiones**: ARS ↔ USD con cualquier tipo de cambio

## Instalación

```bash
pip install mcp-argentina
```

O desde source:

```bash
git clone https://github.com/greydina/mcp-argentina.git
cd mcp-argentina
pip install -e ".[dev]"
```

## Quick Start

### Como servidor MCP

```bash
# Ejecutar servidor stdio
python -m mcp_argentina
```

### Uso directo (sin MCP)

```python
import asyncio
from mcp_argentina.infrastructure.container import Container

async def main():
    c = Container()
    
    # Dólar blue
    blue = await c.repository.obtener_dolar("blue")
    print(f"Blue: ${blue.venta.valor:,.0f}")
    
    # Inflación
    inf = await c.inflacion.obtener_actual()
    print(f"Inflación interanual: {inf.interanual:.1f}%")
    
    # Riesgo país
    riesgo = await c.repository.obtener_riesgo_pais()
    print(f"Riesgo país: {riesgo}")

asyncio.run(main())
```

## MCP Tools

| Tool | Descripción |
|------|-------------|
| `get_dolar` | Cotización de un tipo de dólar específico |
| `get_cotizaciones` | Todas las cotizaciones de dólar |
| `get_historico` | Histórico de cotizaciones (30+ días) |
| `get_inflacion` | Inflación mensual, interanual, acumulada |
| `get_riesgo_pais` | Índice EMBI Argentina |
| `get_moneda` | Cotización de moneda extranjera |
| `get_todas_monedas` | Todas las monedas disponibles |
| `get_variacion` | Variación porcentual en período |
| `get_grafico` | Gráfico ASCII de tendencia |
| `convertir` | Conversión ARS ↔ USD |

## MCP Resources

| URI | Descripción |
|-----|-------------|
| `economia://cotizaciones/actual` | Snapshot JSON de todas las cotizaciones |
| `economia://indicadores/resumen` | Indicadores económicos clave |
| `economia://inflacion/actual` | Datos de inflación actual |

## MCP Prompts

| Prompt | Descripción |
|--------|-------------|
| `analisis_economico` | Análisis de situación económica |
| `comparar_dolares` | Comparación entre tipos de dólar |

## Arquitectura

```
mcp_argentina/
├── domain/                    # Entidades y value objects
│   ├── entities/              # Cotizacion, etc.
│   └── value_objects/         # Precio, Fecha, TipoDolar
│
├── application/               # Lógica de negocio
│   ├── ports/                 # Interfaces (Repository)
│   └── services/              # AlertasService, GraficosService
│
└── infrastructure/            # Implementaciones
    ├── adapters/              # DolarAPI, Historicos, Inflacion, Monedas
    └── mcp/                   # Server, Tools, Resources, Prompts
```

**Clean Architecture**: Dependencias apuntan hacia el dominio.

## Data Sources

100% APIs públicas, cero scraping.

| Fuente | Endpoint | Datos |
|--------|----------|-------|
| [dolarapi.com](https://dolarapi.com) | `/v1/dolares/{tipo}` | Cotizaciones tiempo real (blue, oficial, mep, ccl, cripto, tarjeta, mayorista) |
| [dolarapi.com](https://dolarapi.com) | `/v1/cotizaciones/{moneda}` | Monedas extranjeras (EUR, BRL, UYU, etc.) |
| [argentinadatos.com](https://argentinadatos.com) | `/v1/cotizaciones/dolares/{tipo}` | Histórico de cotizaciones (30+ días) |
| [argentinadatos.com](https://argentinadatos.com) | `/v1/finanzas/indices/inflacion` | Inflación mensual INDEC |
| [argentinadatos.com](https://argentinadatos.com) | `/v1/finanzas/indices/riesgo-pais/ultimo` | Riesgo país (EMBI) |

## Development

```bash
# Tests (sin slow/integration)
pytest -m "not slow"

# Tests con coverage
pytest --cov=mcp_argentina --cov-report=html

# Lint
ruff check .

# Type check
mypy mcp_argentina

# Format
ruff format .
```

## Stats

- ✅ 180 tests
- ✅ 85% coverage
- ✅ Python 3.10, 3.11, 3.12
- ✅ Type-safe (mypy strict)
- ✅ CI/CD GitHub Actions

## Roadmap

- [x] Cotizaciones dólar en tiempo real
- [x] Históricos de cotizaciones
- [x] Inflación (INDEC)
- [x] Riesgo país
- [x] Monedas extranjeras
- [x] Alertas de precio
- [x] Gráficos ASCII
- [x] Conversiones
- [ ] WebSocket para updates real-time
- [ ] Publicar en PyPI
- [ ] Publicar en ClawHub

## License

MIT

---

_Creado por: [greydina](https://github.com/greydina)_  
_Versión: 0.1.0_
