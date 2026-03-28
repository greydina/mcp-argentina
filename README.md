# MCP Argentina

Servidor Model Context Protocol (MCP) para datos económicos de Argentina en tiempo real.

## Features

- 🇦🇷 Cotizaciones del dólar (oficial, blue, MEP, CCL, tarjeta, cripto)
- 📊 Indicadores económicos (inflación, riesgo país)
- 🔄 Datos en tiempo real desde fuentes oficiales
- 🧪 Test coverage 85%+
- 🔒 Type-safe (mypy strict)
- 🐍 Python 3.11+

## Instalación

```bash
# Clonar repo
git clone https://github.com/usuario/mcp-argentina.git
cd mcp-argentina

# Instalar dependencias
pip install -e ".[dev]"
```

## Uso

```python
from mcp_argentina.infrastructure.mcp.server import MCPArgentinaServer

server = MCPArgentinaServer()

# Obtener dólar blue
cotizacion = await server.get_dolar("blue")
print(f"Blue: ${cotizacion['venta']}")

# Obtener todas las cotizaciones
todas = await server.get_cotizaciones()
print(f"Total cotizaciones: {todas['total']}")

await server.close()
```

## Testing

```bash
# Tests unitarios (rápidos)
pytest -m unit

# Tests de integración (contra API real)
pytest -m slow

# Tests E2E
pytest -m e2e

# Todos los tests con coverage
pytest --cov=mcp_argentina --cov-report=html

# Abrir reporte de coverage
open htmlcov/index.html
```

## Desarrollo

```bash
# Linting
ruff check .

# Type checking
mypy mcp_argentina

# Formateo
ruff format .
```

## Arquitectura

```
mcp_argentina/
├── domain/              # Entidades y value objects
├── application/         # Casos de uso y ports
└── infrastructure/      # Adapters y MCP server
```

**Clean Architecture:** Dependencias apuntan hacia el dominio (centro). Infrastructure depende de application, application depende de domain.

## Data Sources

- **dolarapi.com** - Cotizaciones de dólar en tiempo real
- **BCRA** - Indicadores económicos oficiales (próximamente)

## Licencia

MIT License

## Roadmap

- [x] Tests suite completa (85%+ coverage)
- [ ] Tool `get_inflacion`
- [ ] Tool `get_riesgo_pais`
- [ ] Tool `convertir`
- [ ] Resources MCP
- [ ] Prompts MCP
- [ ] Publicar en PyPI
- [ ] Publicar en ClawHub

---

_Creado por: OpenClaw Community_  
_Versión: 0.1.0_
