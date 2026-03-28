# 🛠️ Guía para Contribuidores

Bienvenido! Esta guía explica cómo contribuir a MCP Argentina.

---

## Tabla de Contenidos

1. [Setup de Desarrollo](#setup-de-desarrollo)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Convenciones de Código](#convenciones-de-código)
4. [Testing](#testing)
5. [Contribuir](#contribuir)
6. [Roadmap](#roadmap)

---

## Setup de Desarrollo

### 1. Fork y Clone

```bash
# Fork en GitHub primero, luego:
git clone https://github.com/TU_USUARIO/mcp-argentina.git
cd mcp-argentina
```

### 2. Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -e ".[dev]"
```

Esto instala:
- **Runtime:** `mcp`, `httpx`, `pydantic`, `tenacity`
- **Dev:** `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`, `pre-commit`

### 4. Pre-commit Hooks

```bash
pre-commit install
```

Ejecuta automáticamente antes de cada commit:
- `ruff check` — Linting
- `ruff format` — Formatting
- `mypy` — Type checking
- Tests unitarios

### 5. Verificar Setup

```bash
# Tests
pytest

# Linting
ruff check .

# Type checking
mypy mcp_argentina

# Coverage
pytest --cov=mcp_argentina --cov-report=html
```

Todo debería pasar ✅

---

## Arquitectura del Proyecto

MCP Argentina sigue **Clean Architecture** (Arquitectura Hexagonal) con separación estricta de capas.

### Estructura de Directorios

```
mcp_argentina/
├── domain/                      # Capa de dominio (entidades, value objects)
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── cotizacion.py        # Entidad Cotizacion
│   │   └── indicador.py         # [TODO] Entidad Indicador
│   └── value_objects/
│       ├── __init__.py
│       ├── precio.py            # Value Object Precio
│       └── fecha.py             # Value Object Fecha
├── application/                 # Capa de aplicación (casos de uso)
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── get_dolar.py         # [TODO] Caso de uso GetDolar
│   │   └── convertir.py         # [TODO] Caso de uso Convertir
│   └── ports/                   # Interfaces (abstracciones)
│       ├── __init__.py
│       ├── cotizacion_repository.py  # Interface para repositorio
│       └── indicador_repository.py   # [TODO]
├── infrastructure/              # Capa de infraestructura (implementaciones)
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── dolarapi_adapter.py  # Implementación para dolarapi.com
│   │   ├── bcra_adapter.py      # [TODO] Implementación BCRA
│   │   └── cache_adapter.py     # Cache en memoria
│   └── mcp/
│       ├── __init__.py
│       ├── server.py            # [TODO] MCP server principal
│       ├── tools.py             # [TODO] Definición de tools
│       ├── resources.py         # [TODO] Definición de resources
│       └── prompts.py           # [TODO] Definición de prompts
├── tests/
│   ├── unit/                    # Tests unitarios
│   ├── integration/             # Tests de integración
│   └── e2e/                     # Tests end-to-end
└── docs/                        # Documentación
```

### Capas y Dependencias

```
┌─────────────────────────────────────┐
│   Infrastructure (MCP Server,      │  ← Dependencias externas
│   Adapters, APIs)                   │     (httpx, mcp SDK)
├─────────────────────────────────────┤
│   Application (Use Cases, Ports)   │  ← Lógica de aplicación
├─────────────────────────────────────┤
│   Domain (Entities, Value Objects) │  ← Lógica de negocio pura
└─────────────────────────────────────┘     (sin dependencias)
```

**Regla:** Las capas internas NO pueden depender de las externas.

- ✅ `infrastructure` puede usar `domain` y `application`
- ✅ `application` puede usar `domain`
- ❌ `domain` NO puede importar de `infrastructure` ni `application`

### Domain Layer (Dominio)

**Propósito:** Lógica de negocio pura, sin dependencias externas.

**Entities (Entidades):**
- Tienen identidad única
- Pueden cambiar de estado
- Ejemplo: `Cotizacion`

**Value Objects:**
- Sin identidad propia (dos instancias con mismo valor son iguales)
- Inmutables
- Ejemplo: `Precio`, `Fecha`

**Ejemplo:**

```python
# domain/value_objects/precio.py
from decimal import Decimal
from pydantic import BaseModel

class Precio(BaseModel):
    model_config = {"frozen": True}  # Inmutable
    
    valor: Decimal
    moneda: str
    
    def __add__(self, other):
        if self.moneda != other.moneda:
            raise ValueError("No se pueden sumar precios con monedas diferentes")
        return Precio(valor=self.valor + other.valor, moneda=self.moneda)
```

### Application Layer (Aplicación)

**Propósito:** Casos de uso y puertos (interfaces).

**Use Cases:**
- Orquestan lógica de negocio
- Coordinan múltiples entidades
- Ejemplo: `GetDolarUseCase`, `ConvertirMonedaUseCase`

**Ports (Interfaces):**
- Abstracciones para infraestructura
- Ejemplo: `CotizacionRepository`

**Ejemplo:**

```python
# application/ports/cotizacion_repository.py
from abc import ABC, abstractmethod
from domain.entities.cotizacion import Cotizacion

class CotizacionRepository(ABC):
    @abstractmethod
    async def get_cotizacion(self, casa: str) -> Cotizacion:
        """Obtiene cotización de una casa específica."""
        pass
```

### Infrastructure Layer (Infraestructura)

**Propósito:** Implementaciones concretas de ports.

**Adapters:**
- Implementan interfaces definidas en `application/ports`
- Ejemplo: `DolarAPIAdapter` implementa `CotizacionRepository`

**MCP Server:**
- Expone use cases como MCP tools
- Maneja serialización/deserialización

**Ejemplo:**

```python
# infrastructure/adapters/dolarapi_adapter.py
from application.ports.cotizacion_repository import CotizacionRepository
from domain.entities.cotizacion import Cotizacion

class DolarAPIAdapter(CotizacionRepository):
    async def get_cotizacion(self, casa: str) -> Cotizacion:
        # Implementación concreta usando httpx
        pass
```

---

## Convenciones de Código

### Style Guide

Seguimos [PEP 8](https://peps.python.org/pep-0008/) con algunas preferencias:

- **Line length:** 100 caracteres (no 80)
- **Quotes:** Dobles (`"`) por defecto
- **Imports:** Ordenados con `ruff` (isort)
- **Docstrings:** Google style

### Naming

| Tipo | Convención | Ejemplo |
|------|------------|---------|
| Clases | PascalCase | `DolarAPIAdapter` |
| Funciones | snake_case | `get_dolar()` |
| Variables | snake_case | `cotizacion_actual` |
| Constantes | UPPER_SNAKE_CASE | `BASE_URL` |
| Private | `_prefijo` | `_parse_response()` |

### Type Hints

**SIEMPRE** usar type hints:

```python
# ✅ Correcto
async def get_dolar(casa: str) -> Cotizacion:
    pass

# ❌ Incorrecto
async def get_dolar(casa):
    pass
```

### Docstrings

Usar Google style para todas las funciones públicas:

```python
def convertir(monto: Decimal, desde: str, hacia: str) -> Decimal:
    """
    Convierte un monto entre dos monedas.
    
    Args:
        monto: Cantidad a convertir
        desde: Código de moneda origen (ej: "ARS")
        hacia: Código de moneda destino (ej: "USD")
        
    Returns:
        Monto convertido
        
    Raises:
        ValueError: Si las monedas no son válidas
        
    Example:
        >>> convertir(Decimal("1000"), "ARS", "USD")
        Decimal("0.79")
    """
    pass
```

### Error Handling

**Errores esperados → excepciones específicas:**

```python
# ✅ Correcto
if casa not in CASAS_VALIDAS:
    raise ValueError(f"Casa '{casa}' no válida. Opciones: {CASAS_VALIDAS}")

# ❌ Incorrecto
if casa not in CASAS_VALIDAS:
    return None  # No usar None para indicar errores
```

---

## Testing

### Estructura de Tests

```
tests/
├── unit/                    # Tests unitarios (domain, application)
│   ├── domain/
│   │   ├── test_precio.py
│   │   └── test_cotizacion.py
│   └── application/
│       └── test_use_cases.py
├── integration/             # Tests de integración (adapters)
│   └── test_dolarapi_adapter.py
└── e2e/                     # Tests end-to-end (MCP server)
    └── test_mcp_server.py
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo unitarios
pytest tests/unit/

# Con coverage
pytest --cov=mcp_argentina --cov-report=html

# Tests específicos
pytest tests/unit/domain/test_precio.py -v
```

### Escribir Tests

**Unit Tests:**

```python
# tests/unit/domain/test_precio.py
from decimal import Decimal
import pytest
from mcp_argentina.domain.value_objects.precio import Precio

def test_precio_suma_misma_moneda():
    p1 = Precio(valor=Decimal("100"), moneda="ARS")
    p2 = Precio(valor=Decimal("50"), moneda="ARS")
    resultado = p1 + p2
    assert resultado.valor == Decimal("150")

def test_precio_suma_diferente_moneda_error():
    p1 = Precio(valor=Decimal("100"), moneda="ARS")
    p2 = Precio(valor=Decimal("50"), moneda="USD")
    with pytest.raises(ValueError, match="monedas diferentes"):
        p1 + p2
```

**Integration Tests:**

```python
# tests/integration/test_dolarapi_adapter.py
import pytest
from mcp_argentina.infrastructure.adapters.dolarapi_adapter import DolarAPIAdapter

@pytest.mark.asyncio
async def test_get_dolar_blue():
    async with DolarAPIAdapter() as adapter:
        cotizacion = await adapter.get_dolar("blue")
        assert cotizacion.moneda == "USD"
        assert cotizacion.casa == "blue"
        assert cotizacion.venta.valor > 0
```

### Coverage Goal

**Mínimo:** 85%

```bash
pytest --cov=mcp_argentina --cov-report=term --cov-fail-under=85
```

---

## Contribuir

### Workflow

1. **Fork** el repositorio
2. **Clone** tu fork
3. **Crear rama** para tu feature: `git checkout -b feature/nueva-funcionalidad`
4. **Hacer cambios** siguiendo convenciones
5. **Escribir tests**
6. **Ejecutar tests y linters**
7. **Commit** con mensaje convencional
8. **Push** a tu fork
9. **Abrir Pull Request**

### Commit Messages

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<scope>): <descripción>

[cuerpo opcional]

[footer opcional]
```

**Tipos:**

- `feat:` — Nueva funcionalidad
- `fix:` — Bug fix
- `docs:` — Cambios en documentación
- `test:` — Agregar/modificar tests
- `refactor:` — Refactoring sin cambiar funcionalidad
- `perf:` — Mejora de performance
- `chore:` — Tareas de mantenimiento

**Ejemplos:**

```bash
git commit -m "feat(adapter): add BCRA API support"
git commit -m "fix(precio): handle negative values in subtraction"
git commit -m "docs: update installation guide"
git commit -m "test(adapter): add integration tests for dolarapi"
```

### Pull Request Guidelines

**Título:** Igual que commit message principal

**Descripción debe incluir:**

- ✅ Qué cambia y por qué
- ✅ Link a issue relacionado (si aplica)
- ✅ Screenshots (si hay cambios visuales)
- ✅ Tests agregados/modificados
- ✅ Checklist completado

**Checklist:**

- [ ] Tests pasan (`pytest`)
- [ ] Linting OK (`ruff check`)
- [ ] Type checking OK (`mypy`)
- [ ] Coverage ≥85% (`pytest --cov`)
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado (si es feature/fix)

---

## Roadmap

### v0.2.0 (Próximo)

- [ ] Implementar tool `get_inflacion`
- [ ] Implementar tool `get_riesgo_pais`
- [ ] Implementar tool `convertir`
- [ ] Cache inteligente con TTL por tipo de dato
- [ ] Históricos (últimos 30 días)
- [ ] MCP server funcional (tools básicos)

### v0.3.0

- [ ] Integración BCRA API oficial
- [ ] Datos de inflación por rubro
- [ ] Resource `economia://indicadores/resumen`
- [ ] Prompt `analisis_economico`
- [ ] Alertas de variación (threshold-based)

### v1.0.0 (Production Ready)

- [ ] Publicar en PyPI
- [ ] Publicar en ClawHub
- [ ] Docker image oficial
- [ ] CI/CD completo (GitHub Actions)
- [ ] Monitoreo y logging
- [ ] Documentación completa en mkdocs
- [ ] Rate limiting robusto

---

## Preguntas Frecuentes

### ¿Puedo agregar un nuevo data source?

¡Sí! Crea un nuevo adapter en `infrastructure/adapters/` implementando la interface correspondiente en `application/ports/`.

### ¿Cómo propongo una nueva feature?

Abre un issue en GitHub con:
- Descripción del problema que resuelve
- Ejemplo de uso propuesto
- Posibles implementaciones

### ¿Dónde reporto un bug?

En [GitHub Issues](https://github.com/anibaljasin/mcp-argentina/issues) con:
- Descripción del bug
- Pasos para reproducir
- Comportamiento esperado vs actual
- Versión de Python y mcp-argentina

---

## Recursos

- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [PEP 8 — Style Guide for Python](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

Gracias por contribuir! 🙌
