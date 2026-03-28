# 🔧 Referencia de API

Documentación completa de todos los tools, resources y prompts disponibles en MCP Argentina.

---

## Tools

Los tools son funciones que los agentes pueden llamar para obtener datos específicos.

### `get_dolar`

Obtiene la cotización del dólar para una casa específica.

**Parámetros:**

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `casa` | string | ✅ | Tipo de cotización: `blue`, `oficial`, `mep`, `ccl`, `cripto`, `tarjeta`, `mayorista` |

**Retorna:**

```json
{
  "moneda": "USD",
  "casa": "blue",
  "nombre": "Dólar Blue",
  "compra": 1245.00,
  "venta": 1265.00,
  "fechaActualizacion": "2026-03-28T15:30:00Z"
}
```

**Ejemplo de uso (Claude):**

```
cuánto está el dólar blue?
```

**Ejemplo de uso (Python):**

```python
async with DolarAPIAdapter() as adapter:
    cotizacion = await adapter.get_dolar("blue")
    print(f"Venta: ${cotizacion.venta.valor}")
```

**Errores:**

- `ValueError` — Casa inválida
- `ConnectionError` — Error de red después de reintentos
- `httpx.HTTPStatusError` — Error HTTP (ej: 404, 500)

---

### `get_cotizaciones`

Obtiene todas las cotizaciones disponibles del dólar en una sola llamada.

**Parámetros:**

Ninguno.

**Retorna:**

```json
[
  {
    "moneda": "USD",
    "casa": "oficial",
    "nombre": "Dólar Oficial",
    "compra": 850.00,
    "venta": 890.00,
    "fechaActualizacion": "2026-03-28T15:30:00Z"
  },
  {
    "moneda": "USD",
    "casa": "blue",
    "nombre": "Dólar Blue",
    "compra": 1245.00,
    "venta": 1265.00,
    "fechaActualizacion": "2026-03-28T15:31:00Z"
  }
  // ... más cotizaciones
]
```

**Ejemplo de uso (Claude):**

```
mostrá todas las cotizaciones del dólar
```

**Ejemplo de uso (Python):**

```python
async with DolarAPIAdapter() as adapter:
    todas = await adapter.get_todas_las_cotizaciones()
    for cot in todas:
        print(f"{cot.nombre}: ${cot.venta.valor}")
```

---

### `get_cotizacion_moneda`

Obtiene la cotización de una moneda extranjera específica (ej: EUR, BRL).

**Parámetros:**

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `moneda` | string | ✅ | Código de moneda (lowercase): `eur`, `brl`, `clp`, `uyu` |

**Retorna:**

```json
{
  "moneda": "EUR",
  "casa": "oficial",
  "nombre": "Euro",
  "compra": 1050.00,
  "venta": 1070.00,
  "fechaActualizacion": "2026-03-28T15:30:00Z"
}
```

**Ejemplo de uso (Claude):**

```
a cuánto está el euro?
```

**Ejemplo de uso (Python):**

```python
async with DolarAPIAdapter() as adapter:
    euro = await adapter.get_cotizacion_moneda("eur")
    print(f"Euro: ${euro.venta.valor}")
```

**Errores:**

- `ValueError` — Moneda no encontrada o inválida
- `ConnectionError` — Error de red

---

### `get_inflacion`

*[Próximamente en v0.2.0]*

Obtiene datos de inflación mensual, anual y acumulada.

**Parámetros:**

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `periodo` | string | ❌ | Formato `YYYY-MM`. Default: último mes disponible |

**Retorna:**

```json
{
  "periodo": "2026-02",
  "mensual": 20.6,
  "anual": 276.4,
  "acumulada": 25.2,
  "fuente": "INDEC",
  "fechaPublicacion": "2026-03-15T10:00:00Z"
}
```

---

### `get_riesgo_pais`

*[Próximamente en v0.2.0]*

Obtiene el riesgo país actual e histórico.

**Parámetros:**

Ninguno.

**Retorna:**

```json
{
  "valor": 1824,
  "variacion": -12,
  "variacionPorcentual": -0.65,
  "fechaActualizacion": "2026-03-28T15:30:00Z"
}
```

---

### `convertir`

*[Próximamente en v0.2.0]*

Convierte entre ARS y USD usando un tipo de cambio específico.

**Parámetros:**

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| `monto` | number | ✅ | Cantidad a convertir |
| `desde` | string | ✅ | Moneda origen: `ARS` o `USD` |
| `hacia` | string | ✅ | Moneda destino: `ARS` o `USD` |
| `tipo_cambio` | string | ✅ | Tipo de cambio a usar: `blue`, `oficial`, `mep`, `ccl` |

**Retorna:**

```json
{
  "montoOriginal": 100.00,
  "monedaOriginal": "USD",
  "montoConvertido": 126500.00,
  "monedaDestino": "ARS",
  "tipoCambio": 1265.00,
  "tipoCambioNombre": "Dólar Blue (venta)"
}
```

**Ejemplo:**

```
cuántos dólares son 50,000 pesos al tipo blue?
```

---

## Resources

Los resources son datos estructurados que los agentes pueden leer directamente (sin ejecutar una función).

### `economia://cotizaciones/actual`

Snapshot de todas las cotizaciones actuales.

**Formato:**

```json
{
  "timestamp": "2026-03-28T15:30:00Z",
  "cotizaciones": [
    {
      "moneda": "USD",
      "casa": "blue",
      "nombre": "Dólar Blue",
      "compra": 1245.00,
      "venta": 1265.00
    }
    // ... más cotizaciones
  ]
}
```

---

### `economia://indicadores/resumen`

*[Próximamente]*

Resumen de indicadores económicos clave.

**Formato:**

```json
{
  "timestamp": "2026-03-28T15:30:00Z",
  "dolarBlue": 1265.00,
  "riesgoPais": 1824,
  "inflacionMensual": 20.6,
  "inflacionAnual": 276.4
}
```

---

## Prompts

Los prompts son templates predefinidos que los agentes pueden usar para tareas comunes.

### `analisis_economico`

*[Próximamente]*

Template para análisis completo de la situación económica argentina.

**Variables:**

- `periodo` — Periodo a analizar (ej: "último mes", "último trimestre")
- `incluir_proyecciones` — Boolean, incluir proyecciones futuras

**Output esperado:**

Análisis estructurado con:
- Resumen de cotizaciones
- Variación de indicadores
- Análisis de tendencias
- Proyecciones (si aplica)

---

### `comparar_dolares`

*[Próximamente]*

Compara diferentes tipos de cambio y calcula el "dólar implícito".

**Variables:**

- `tipos` — Lista de tipos a comparar (default: todos)

**Output esperado:**

Tabla comparativa con:
- Cotización de cada tipo
- Spread con dólar oficial
- Brecha porcentual

---

## Tipos de Datos

### Cotizacion

Entidad que representa una cotización de moneda.

```python
@dataclass
class Cotizacion:
    moneda: str                    # Código de moneda (USD, EUR, etc.)
    casa: str                      # Tipo de cotización (blue, oficial, etc.)
    nombre: str                    # Nombre descriptivo
    compra: Precio                 # Precio de compra
    venta: Precio                  # Precio de venta
    fecha_actualizacion: datetime  # Última actualización
```

### Precio

Value object que representa un valor monetario con precisión decimal.

```python
@dataclass(frozen=True)
class Precio:
    valor: Decimal  # Valor numérico (usa Decimal para precisión)
    moneda: str     # Código ISO 4217 (ARS, USD, EUR)
    
    # Operaciones: +, -, *, /, comparaciones
```

**Características:**

- Inmutable (`frozen=True`)
- Validación automática (valor no negativo)
- Aritmética segura entre precios de misma moneda
- Formato string: `"1265.00 ARS"`

---

## Códigos de Error

### ValueError

**Causa:** Parámetro inválido (casa no válida, moneda no encontrada)

**Manejo:**

```python
try:
    await adapter.get_dolar("invalid")
except ValueError as e:
    print(f"Error de validación: {e}")
```

### ConnectionError

**Causa:** Error de red después de 3 reintentos

**Manejo:**

```python
try:
    await adapter.get_dolar("blue")
except ConnectionError as e:
    print(f"Error de conexión: {e}")
    # Implementar fallback o retry manual
```

### httpx.HTTPStatusError

**Causa:** Error HTTP (404, 500, etc.)

**Manejo:**

```python
try:
    await adapter.get_cotizacion_moneda("xyz")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        print("Moneda no encontrada")
    else:
        print(f"Error del servidor: {e}")
```

---

## Rate Limits

**dolarapi.com:**
- Sin rate limit oficial documentado
- Recomendado: max 1 request/segundo
- Implementar cache local para reducir llamadas

**BCRA API:**
- 100 requests/minuto por IP (cuando se implemente)

---

## Latencias Típicas

| Operación | Latencia |
|-----------|----------|
| `get_dolar` | 100-300ms |
| `get_cotizaciones` | 200-400ms |
| `get_cotizacion_moneda` | 100-300ms |

*Nota: Latencias medidas desde Argentina. Agregar ~50-100ms desde otros países.*

---

## Versionado

MCP Argentina sigue [Semantic Versioning](https://semver.org/):

- **MAJOR:** Cambios incompatibles en API
- **MINOR:** Nueva funcionalidad compatible
- **PATCH:** Bug fixes

Versión actual: **0.1.0** (MVP)

---

## Changelog

### v0.1.0 (2026-03-28)

- ✨ Implementación inicial
- 🔧 Tools: `get_dolar`, `get_cotizaciones`, `get_cotizacion_moneda`
- 📊 Adapter para dolarapi.com
- 🧪 Clean Architecture con domain/application/infrastructure
- 📝 Documentación completa en español

### Roadmap

- **v0.2.0:** Cache, históricos, inflación, riesgo país
- **v0.3.0:** BCRA API, alertas de variación
- **v1.0.0:** PyPI, ClawHub, Docker

---

## Siguientes Pasos

- [Guía de Uso](uso.md) — Ejemplos prácticos
- [Guía de Desarrollo](desarrollo.md) — Contribuir y extender
