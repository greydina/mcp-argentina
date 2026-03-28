# MCP Argentina - Quickstart

## Verificación Rápida

### 1. Instalación

```bash
cd /home/ubuntu/.openclaw/workspace/mcp-argentina
pip install -e .
```

### 2. Test Manual de Tools

Probá los tools directamente en Python:

```python
import asyncio
from mcp_argentina.infrastructure.mcp import tools

# Test get_dolar
async def test_basic():
    # Obtener dólar blue
    blue = await tools.get_dolar("blue")
    print(f"Dólar Blue: ${blue['venta']}")
    
    # Obtener todas las cotizaciones
    cotizaciones = await tools.get_cotizaciones()
    print(f"Cotizaciones disponibles: {list(cotizaciones.keys())}")
    
    # Convertir USD a ARS
    conversion = await tools.convertir(
        monto=100,
        de="USD",
        a="ARS",
        tipo_cambio="blue"
    )
    print(f"100 USD = ${conversion['monto_convertido']} ARS")

asyncio.run(test_basic())
```

### 3. Ejecutar el Servidor

```bash
# Forma 1: Script directo
python run_server.py

# Forma 2: Comando instalado
mcp-argentina
```

El servidor se ejecuta en modo stdio (comunicación vía stdin/stdout) para MCP.

### 4. Tests de Integración

```bash
# Instalar pytest si no está
pip install pytest pytest-asyncio

# Ejecutar tests
pytest tests/integration/test_mcp_tools.py -v
```

### 5. Verificar Estructura

```bash
# Listar módulos
find mcp_argentina/infrastructure/mcp -name "*.py"

# Debería mostrar:
# mcp_argentina/infrastructure/mcp/__init__.py
# mcp_argentina/infrastructure/mcp/server.py
# mcp_argentina/infrastructure/mcp/tools.py
# mcp_argentina/infrastructure/mcp/resources.py
# mcp_argentina/infrastructure/mcp/prompts.py
```

## Integración con OpenClaw

### Configuración

Agregar a `~/.openclaw/config.json` o `openclaw.json` en tu proyecto:

```json
{
  "mcp": {
    "servers": {
      "mcp-argentina": {
        "command": "python",
        "args": [
          "/home/ubuntu/.openclaw/workspace/mcp-argentina/run_server.py"
        ]
      }
    }
  }
}
```

### Uso desde OpenClaw

Luego de configurar, OpenClaw tendrá acceso automático a:

**Tools:**
- `get_dolar` - Obtener cotización específica
- `get_cotizaciones` - Todas las cotizaciones
- `convertir` - Conversión ARS/USD

**Resources:**
- `economia://cotizaciones/actual`
- `economia://indicadores/resumen`

**Prompts:**
- `analisis_economico`
- `comparar_dolares`

### Ejemplo de Uso

```python
# Desde un agente de OpenClaw
"Cuál es el precio del dólar blue?"
# → Llamará automáticamente a get_dolar("blue")

"Convertí 500 USD a pesos al blue"
# → Llamará a convertir(monto=500, de="USD", a="ARS", tipo_cambio="blue")
```

## Troubleshooting

### Error: Module 'mcp' not found

```bash
pip install mcp httpx pydantic
```

### Error: API timeout

La API de dolarapi.com puede ser lenta. El timeout está configurado en 10 segundos.

### Error: Invalid tipo de dólar

Tipos válidos: `blue`, `oficial`, `mep`, `ccl`, `cripto`, `tarjeta`

## Próximos Pasos

1. **Tests unitarios**: Agregar tests para validación de inputs
2. **Cache**: Implementar cache local para reducir llamadas a la API
3. **Históricos**: Agregar endpoint para datos históricos
4. **Inflación**: Integrar datos de inflación del BCRA

---

**Status**: ✅ MVP completado  
**Fecha**: 2026-03-28  
**Versión**: 0.1.0
