# MCP Argentina 🇦🇷

Servidor Model Context Protocol (MCP) para consultar datos económicos de Argentina en tiempo real.

## Características

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
git clone https://github.com/greydina/mcp-argentina
cd mcp-argentina
pip install -e .
```

## Integración con Clientes MCP

Después de instalar, necesitás configurar tu cliente MCP para que ejecute el servidor.

### Claude Desktop

Editá `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) o `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "mcp-argentina": {
      "command": "python",
      "args": ["-m", "mcp_argentina"]
    }
  }
}
```

Si usás un virtualenv:

```json
{
  "mcpServers": {
    "mcp-argentina": {
      "command": "/ruta/a/tu/venv/bin/python",
      "args": ["-m", "mcp_argentina"]
    }
  }
}
```

### Cursor

Editá `.cursor/mcp.json` en tu proyecto o `~/.cursor/mcp.json` global:

```json
{
  "mcpServers": {
    "mcp-argentina": {
      "command": "python",
      "args": ["-m", "mcp_argentina"]
    }
  }
}
```

### Cline (VS Code)

Agregá en la configuración de Cline:

```json
{
  "mcp-argentina": {
    "command": "python",
    "args": ["-m", "mcp_argentina"]
  }
}
```

### OpenClaw

Agregá en `openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "mcp-argentina": {
        "command": "python",
        "args": ["-m", "mcp_argentina"]
      }
    }
  }
}
```

### Verificar instalación

Después de configurar, reiniciá tu cliente. Deberías ver las herramientas disponibles:
- `get_dolar`
- `get_cotizaciones`
- `get_inflacion`
- `get_riesgo_pais`
- etc.

Probá con: "¿Cuánto está el dólar blue?"

## Inicio Rápido

### Ejecutar servidor manualmente (debug)

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
    print(f"💵 Blue: ${blue.venta.valor:,.0f}")
    
    # Inflación
    inf = await c.inflacion.obtener_actual()
    print(f"📊 Inflación interanual: {inf.interanual:.1f}%")
    
    # Riesgo país
    riesgo = await c.repository.obtener_riesgo_pais()
    print(f"🌡️ Riesgo país: {riesgo}")
    
    # Euro
    euro = await c.monedas.obtener_moneda("EUR")
    print(f"💶 Euro: ${euro.venta:,.0f}")

asyncio.run(main())
```

**Salida:**
```
💵 Blue: $1,415
📊 Inflación interanual: 33.0%
🌡️ Riesgo país: 615
💶 Euro: $1,593
```

## Ejemplos

### Obtener todas las cotizaciones

```python
cotizaciones = await c.repository.obtener_todas()
for cot in cotizaciones:
    print(f"{cot.nombre}: ${cot.venta.valor:,.0f}")
```

**Salida:**
```
Oficial: $1,000
Blue: $1,415
Bolsa: $1,380
Contado con liquidación: $1,390
Mayorista: $1,005
Cripto: $1,410
Tarjeta: $1,600
```

### Histórico del dólar blue

```python
historicos = await c.historicos.obtener_historico_dolar("blue", dias=7)
for h in historicos:
    print(f"{h.fecha}: ${h.venta:,.0f}")
```

**Salida:**
```
2026-03-22: $1,425
2026-03-23: $1,420
2026-03-24: $1,418
2026-03-25: $1,415
2026-03-26: $1,410
2026-03-27: $1,415
2026-03-28: $1,415
```

### Variación porcentual

```python
var = await c.historicos.obtener_variacion_dolar("blue", dias=7)
print(f"Variación 7 días: {var['variacion_porcentual']:+.1f}%")
```

**Salida:**
```
Variación 7 días: -0.7%
```

### Conversión USD → ARS

```python
blue = await c.repository.obtener_dolar("blue")
usd = 100
ars = usd * float(blue.venta.valor)
print(f"USD {usd} = ARS {ars:,.0f} (al blue)")
```

**Salida:**
```
USD 100 = ARS 141,500 (al blue)
```

### Gráfico ASCII de tendencia

```python
from mcp_argentina.application.services.graficos_service import PuntoGrafico

historicos = await c.historicos.obtener_historico_dolar("blue", dias=30)
puntos = [PuntoGrafico(fecha=h.fecha, valor=float(h.venta)) for h in historicos]
grafico = c.graficos.generar_linea(puntos, titulo="Dólar Blue (30 días)")
print(grafico)
```

**Salida:**
```
📊 Dólar Blue (30 días)

Max: $1,450
▅▆▇█▇▆▅▄▃▂▁▁▂▃▄▅▆▅▄▃▂▂▃▄▄▃▂▁▁▁
Min: $1,400
27/02 28/03
📉 -2.4%
```

## Herramientas MCP

| Herramienta | Descripción |
|-------------|-------------|
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

## Resources MCP

| URI | Descripción |
|-----|-------------|
| `economia://cotizaciones/actual` | Snapshot JSON de todas las cotizaciones |
| `economia://indicadores/resumen` | Indicadores económicos clave |
| `economia://inflacion/actual` | Datos de inflación actual |

## Prompts MCP

| Prompt | Descripción |
|--------|-------------|
| `analisis_economico` | Análisis de situación económica |
| `comparar_dolares` | Comparación entre tipos de dólar |

## Fuentes de Datos

100% APIs públicas, cero scraping.

| Fuente | Endpoint | Datos |
|--------|----------|-------|
| [dolarapi.com](https://dolarapi.com) | `/v1/dolares/{tipo}` | Cotizaciones tiempo real |
| [dolarapi.com](https://dolarapi.com) | `/v1/cotizaciones/{moneda}` | Monedas extranjeras |
| [argentinadatos.com](https://argentinadatos.com) | `/v1/cotizaciones/dolares/{tipo}` | Histórico de cotizaciones |
| [argentinadatos.com](https://argentinadatos.com) | `/v1/finanzas/indices/inflacion` | Inflación mensual INDEC |
| [argentinadatos.com](https://argentinadatos.com) | `/v1/finanzas/indices/riesgo-pais/ultimo` | Riesgo país (EMBI) |

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
    ├── errors.py              # Excepciones personalizadas
    ├── logging.py             # Logging estructurado
    ├── retry.py               # Retry con backoff exponencial
    └── mcp/                   # Server, Tools, Resources, Prompts
```

**Clean Architecture**: Dependencias apuntan hacia el dominio.

## Desarrollo

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
- ✅ 78% coverage
- ✅ Python 3.10, 3.11, 3.12
- ✅ Type-safe (mypy)
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
- [x] Logging estructurado
- [x] Retry con backoff
- [ ] WebSocket para updates real-time
- [ ] Publicar en PyPI
- [ ] Publicar en ClawHub

## Licencia

MIT

---

_Creado por: [greydina](https://github.com/greydina)_  
_Versión: 0.1.0_
