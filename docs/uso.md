# 📖 Guía de Uso

Esta guía muestra cómo usar MCP Argentina en diferentes contextos.

---

## Uso desde Claude Desktop

Una vez instalado el servidor MCP (ver [Guía de Instalación](instalacion.md)), simplemente preguntale a Claude sobre economía argentina.

### Ejemplos de Prompts

**Cotización del dólar:**
```
cuánto está el dólar blue?
```

**Comparar tipos de cambio:**
```
mostrá todas las cotizaciones del dólar
```

**Conversión de moneda:**
```
cuántos dólares son 50,000 pesos argentinos al tipo blue?
```

**Análisis económico:**
```
hacé un resumen de la situación económica actual: dólar, inflación y riesgo país
```

Claude utilizará automáticamente los tools de MCP Argentina para responder.

---

## Uso desde OpenClaw

MCP Argentina se integra con OpenClaw para automatizaciones y agentes.

### Consultar desde Chat

```
@dina cuánto está el dólar oficial?
```

### Automatización con Heartbeats

Agregar a `HEARTBEAT.md`:

```markdown
- Si el dólar blue sube más de 5% en un día, avisame
- Revisar riesgo país cada 24h, alertar si >2000
```

### Uso Programático (Skills)

```python
# Desde un skill de OpenClaw
async def check_dolar_blue():
    # Usar MCP tool directamente
    result = await mcp_call("argentina", "get_dolar", {"casa": "blue"})
    return result
```

---

## Uso como Librería Python

MCP Argentina puede usarse directamente como librería sin servidor MCP.

### Ejemplo Básico

```python
import asyncio
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter

async def main():
    async with DolarAPIAdapter() as adapter:
        # Obtener dólar blue
        blue = await adapter.get_dolar("blue")
        print(f"Dólar Blue: ${blue.venta.valor}")
        
        # Obtener todas las cotizaciones
        todas = await adapter.get_todas_las_cotizaciones()
        for cot in todas:
            print(f"{cot.nombre}: ${cot.venta.valor}")

asyncio.run(main())
```

### Manejo de Errores

```python
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter

async def get_dolar_safe(casa: str):
    try:
        async with DolarAPIAdapter() as adapter:
            return await adapter.get_dolar(casa)
    except ValueError as e:
        print(f"Casa inválida: {e}")
    except ConnectionError as e:
        print(f"Error de conexión: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
```

### Uso con Cache

```python
from mcp_argentina.infrastructure.adapters.cache_adapter import CacheAdapter
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter

async def get_dolar_cached(casa: str):
    cache = CacheAdapter(ttl_seconds=300)  # 5 minutos
    
    # Intentar desde cache
    cached = await cache.get(f"dolar:{casa}")
    if cached:
        return cached
    
    # Si no está en cache, consultar API
    async with DolarAPIAdapter() as adapter:
        result = await adapter.get_dolar(casa)
        await cache.set(f"dolar:{casa}", result)
        return result
```

---

## Casos de Uso Reales

### 1. Bot de Telegram con Alertas

```python
import asyncio
from telegram import Bot
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter

async def alertar_dolar_alto(bot: Bot, chat_id: int, umbral: float):
    async with DolarAPIAdapter() as adapter:
        blue = await adapter.get_dolar("blue")
        
        if blue.venta.valor > umbral:
            await bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ Alerta: Dólar blue en ${blue.venta.valor} (umbral: ${umbral})"
            )

# Ejecutar cada hora
while True:
    await alertar_dolar_alto(bot, chat_id=123456, umbral=1300)
    await asyncio.sleep(3600)
```

### 2. Dashboard en Streamlit

```python
import streamlit as st
import asyncio
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter

st.title("💱 Cotizaciones en Vivo")

async def load_data():
    async with DolarAPIAdapter() as adapter:
        return await adapter.get_todas_las_cotizaciones()

cotizaciones = asyncio.run(load_data())

for cot in cotizaciones:
    st.metric(
        label=cot.nombre,
        value=f"${cot.venta.valor:.2f}",
        delta=f"Compra: ${cot.compra.valor:.2f}"
    )
```

### 3. Script de Monitoreo

```python
#!/usr/bin/env python
"""
Monitor dólar blue y enviar email si supera umbral.
Ejecutar con cron: 0 */6 * * * /path/to/monitor.py
"""
import asyncio
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter
import smtplib

UMBRAL = 1300
EMAIL_TO = "tu@email.com"

async def main():
    async with DolarAPIAdapter() as adapter:
        blue = await adapter.get_dolar("blue")
        
        if blue.venta.valor > UMBRAL:
            msg = f"Dólar blue: ${blue.venta.valor} (umbral: ${UMBRAL})"
            # Enviar email (implementación básica)
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login("tu@gmail.com", "password")
                smtp.sendmail("tu@gmail.com", EMAIL_TO, msg)
            print(f"Alerta enviada: {msg}")
        else:
            print(f"Dólar blue: ${blue.venta.valor} (OK)")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Mejores Prácticas

### 1. Usar Context Managers

✅ **Correcto:**
```python
async with DolarAPIAdapter() as adapter:
    result = await adapter.get_dolar("blue")
```

❌ **Incorrecto:**
```python
adapter = DolarAPIAdapter()  # Cliente no inicializado
result = await adapter.get_dolar("blue")  # Falla!
```

### 2. Manejar Errores Específicos

```python
try:
    cotizacion = await adapter.get_dolar("blue")
except ValueError:
    # Casa inválida
    pass
except ConnectionError:
    # Error de red - reintentar?
    pass
```

### 3. Implementar Rate Limiting

```python
import asyncio
from time import time

last_call = {}

async def rate_limited_call(casa: str, min_interval: float = 60):
    now = time()
    if casa in last_call and (now - last_call[casa]) < min_interval:
        await asyncio.sleep(min_interval - (now - last_call[casa]))
    
    async with DolarAPIAdapter() as adapter:
        result = await adapter.get_dolar(casa)
        last_call[casa] = time()
        return result
```

### 4. Usar Cache para Reducir Llamadas

```python
# Datos que cambian cada 5-10 minutos
TTL_COTIZACIONES = 300  # 5 minutos

# Datos que cambian cada hora
TTL_RIESGO_PAIS = 3600  # 1 hora

# Datos que cambian mensualmente
TTL_INFLACION = 86400  # 24 horas
```

---

## Debugging

### Ver Request/Response Raw

```python
import logging

# Habilitar logs de httpx
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("httpx")
logger.setLevel(logging.DEBUG)
```

### Medir Tiempos de Respuesta

```python
from time import time

start = time()
async with DolarAPIAdapter() as adapter:
    result = await adapter.get_dolar("blue")
elapsed = time() - start

print(f"Request completado en {elapsed:.2f}s")
```

---

## Preguntas Frecuentes

### ¿Cada cuánto se actualizan los datos?

- **Cotizaciones:** Cada 1-5 minutos (depende de dolarapi.com)
- **Riesgo país:** Cada 15-30 minutos
- **Inflación:** Mensual (INDEC publica ~día 15)

### ¿Hay límite de requests?

dolarapi.com no tiene rate limiting estricto, pero se recomienda:
- No más de 1 request por segundo
- Usar cache para datos que cambian lentamente

### ¿Funciona sin internet?

No, MCP Argentina consulta APIs externas en tiempo real. Para uso offline, implementar cache persistente.

### ¿Qué pasa si dolarapi.com está caído?

El adapter tiene retry automático (3 intentos con exponential backoff). Si falla después de reintentar, lanza `ConnectionError`.

---

## Siguientes Pasos

- [Referencia de API](api.md) — Ver todos los tools y parámetros
- [Guía de Desarrollo](desarrollo.md) — Contribuir al proyecto
- [Ejemplos en GitHub](https://github.com/anibaljasin/mcp-argentina/tree/main/examples) — Más ejemplos
