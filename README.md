# MCP Argentina 🇦🇷

Servidor [Model Context Protocol (MCP)](https://modelcontextprotocol.io) para datos económicos de Argentina en tiempo real.

## Características

- **Tools**: Consulta cotizaciones de dólar (blue, oficial, MEP, CCL, cripto, tarjeta) y conversión ARS/USD
- **Resources**: Acceso a snapshots de cotizaciones e indicadores económicos
- **Prompts**: Templates para análisis económico estructurado

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/yourusername/mcp-argentina.git
cd mcp-argentina

# Instalar dependencias
pip install -e .

# O con dependencias de desarrollo
pip install -e ".[dev]"
```

## Uso

### Ejecutar el servidor

```bash
# Directamente con Python
python run_server.py

# O usando el comando instalado
mcp-argentina
```

### Configuración en Claude Desktop

Agregar a `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-argentina": {
      "command": "python",
      "args": ["/ruta/a/mcp-argentina/run_server.py"]
    }
  }
}
```

### Configuración en OpenClaw

Agregar a `~/.openclaw/config.json`:

```json
{
  "mcp": {
    "servers": {
      "mcp-argentina": {
        "command": "python",
        "args": ["/ruta/a/mcp-argentina/run_server.py"]
      }
    }
  }
}
```

## Tools Disponibles

### `get_dolar`

Obtiene la cotización de un tipo específico de dólar.

```python
# Ejemplo de uso desde un cliente MCP
result = await client.call_tool("get_dolar", {"tipo": "blue"})
# Retorna: {"tipo": "blue", "compra": 1150, "venta": 1170, "fecha": "..."}
```

**Parámetros:**
- `tipo` (string, requerido): Tipo de dólar - `"blue"`, `"oficial"`, `"mep"`, `"ccl"`, `"cripto"`, `"tarjeta"`

### `get_cotizaciones`

Obtiene todas las cotizaciones disponibles en una sola llamada.

```python
result = await client.call_tool("get_cotizaciones", {})
# Retorna: {"blue": {...}, "oficial": {...}, "mep": {...}, ...}
```

### `convertir`

Convierte un monto entre ARS y USD usando un tipo de cambio específico.

```python
result = await client.call_tool("convertir", {
    "monto": 1000,
    "de": "USD",
    "a": "ARS",
    "tipo_cambio": "blue"
})
# Retorna: {"monto_original": 1000, "monto_convertido": 1170000, ...}
```

**Parámetros:**
- `monto` (float, requerido): Cantidad a convertir (> 0)
- `de` (string, requerido): Moneda origen - `"ARS"` o `"USD"`
- `a` (string, requerido): Moneda destino - `"ARS"` o `"USD"`
- `tipo_cambio` (string, requerido): Tipo de cambio - `"blue"`, `"oficial"`, `"mep"`, `"ccl"`

## Resources Disponibles

### `economia://cotizaciones/actual`

Snapshot de todas las cotizaciones actuales con resumen de indicadores clave.

### `economia://indicadores/resumen`

Resumen de indicadores económicos principales de Argentina.

## Prompts Disponibles

### `analisis_economico`

Template para análisis de la situación económica argentina.

**Argumentos:**
- `enfoque` (opcional): `"general"`, `"mercado_cambiario"`, `"brecha"`, `"tendencias"`

### `comparar_dolares`

Template para comparar diferentes tipos de dólar.

**Argumentos:**
- `tipos` (requerido): Lista de tipos separados por coma (ej: `"blue,oficial,mep"`)

## Fuente de Datos

- **dolarapi.com**: API pública para cotizaciones de dólar en Argentina
- Actualización: ~5 minutos
- Sin autenticación requerida

## Desarrollo

### Estructura del proyecto

```
mcp_argentina/
├── infrastructure/
│   └── mcp/
│       ├── server.py      # Servidor MCP principal
│       ├── tools.py       # Implementación de tools
│       ├── resources.py   # Implementación de resources
│       └── prompts.py     # Definición de prompts
```

### Tests

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=mcp_argentina --cov-report=html
```

### Linting

```bash
# Ruff
ruff check .

# MyPy
mypy mcp_argentina/
```

## Licencia

MIT License - Ver archivo LICENSE para detalles.

## Contribuciones

Contribuciones bienvenidas! Por favor abre un issue o PR.

---

**Versión**: 0.1.0  
**Última actualización**: 2026-03-28
