# Technical Debt Analysis

## Current State (2026-03-29)

| Metric | Value | Target |
|--------|-------|--------|
| Test Coverage | 85% | 90%+ |
| MyPy Errors | 49 | 0 |
| Lines of Code | ~6000 | - |
| Test Count | 180 | - |

## Critical Issues

### 1. Type Safety (HIGH)

**Problem**: 49 mypy errors, mostly in `server.py`.

**Root Causes**:
- MCP SDK decorators are untyped (`@server.list_tools()`, etc.)
- Generic types missing parameters
- Dict return types inconsistent
- Missing return type annotations

**Impact**: Runtime type errors possible, IDE support degraded.

**Fix Effort**: 4-6 hours

**Solution**:
```python
# Before
@server.list_tools()
async def list_tools() -> list[Tool]:

# After - use type: ignore for untyped decorators
@server.list_tools()  # type: ignore[misc]
async def list_tools() -> list[Tool]:
```

### 2. Duplicated API Logic (MEDIUM)

**Problem**: `get_moneda` tool references `Cotizacion.moneda` which doesn't exist.

**Location**: `server.py:264`

**Impact**: Tool crashes at runtime.

**Fix**: Use correct attribute from `CotizacionMoneda` dataclass.

### 3. Inconsistent Error Handling (MEDIUM)

**Problem**: Some adapters return None on error, others raise exceptions.

**Examples**:
- `DolarAPIAdapter.obtener_dolar()` → raises `ValueError`
- `HistoricosAdapter.obtener_historico_dolar()` → returns empty list
- `InflacionAdapter.obtener_actual()` → raises on HTTP error

**Impact**: Inconsistent behavior for callers, harder to handle errors.

**Solution**: Define clear error strategy:
1. Domain errors → raise custom exceptions
2. Infrastructure errors → wrap in `APIError`
3. Empty results → return empty collections, not None

### 4. Container Singleton Anti-Pattern (LOW)

**Problem**: `Container` uses singleton pattern with mutable state.

**Issues**:
- Hard to test in isolation
- Global state makes debugging harder
- Can't have multiple containers with different configs

**Solution**: Inject container instead of using singleton, or at least make `reset()` thread-safe.

### 5. Large `server.py` (LOW)

**Problem**: `server.py` is 514 lines with all tools, resources, and prompts.

**Impact**: Hard to navigate, test, and maintain.

**Solution**: Split into modules:
```
mcp/
├── server.py          # Main server setup
├── tools/
│   ├── cotizaciones.py
│   ├── historicos.py
│   └── indicadores.py
├── resources.py
└── prompts.py
```

## Coverage Gaps

### Untested Code (15%)

| File | Coverage | Missing |
|------|----------|---------|
| `historicos_adapter.py` | 63% | Error paths, edge cases |
| `server.py` | 68% | Resource reads, prompts |
| `dolarapi_adapter.py` | 74% | Timeout, retry logic |
| `cache_adapter.py` | 77% | TTL expiry edge cases |
| `precio.py` | 78% | Arithmetic operations |

### Missing Test Types

- [ ] Load/stress tests
- [ ] Timeout behavior tests
- [ ] Rate limiting tests
- [ ] Concurrent access tests

## Architectural Debt

### 1. No Retry/Circuit Breaker

External APIs can fail. No retry logic or circuit breaker pattern.

**Risk**: Single API failure crashes entire server.

**Solution**: Add `tenacity` for retries, implement circuit breaker.

### 2. No Rate Limiting

No protection against API rate limits.

**Risk**: Getting blocked by dolarapi.com/argentinadatos.com.

**Solution**: Add rate limiter with token bucket algorithm.

### 3. Cache Not Persisted

Cache is in-memory only. Lost on restart.

**Impact**: Cold start makes many API calls.

**Solution**: Add Redis/SQLite backing for cache persistence.

## Priority Matrix

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Type safety (mypy) | HIGH | MEDIUM | 1 |
| `get_moneda` crash | HIGH | LOW | 1 |
| Retry logic | HIGH | MEDIUM | 2 |
| Error handling consistency | MEDIUM | MEDIUM | 3 |
| Rate limiting | MEDIUM | MEDIUM | 3 |
| Split server.py | LOW | MEDIUM | 4 |
| Container singleton | LOW | LOW | 5 |
| Persist cache | LOW | HIGH | 5 |

## Action Plan

### Sprint 1 (4h)
1. Fix `get_moneda` crash
2. Add `# type: ignore` for MCP SDK decorators
3. Fix remaining mypy errors

### Sprint 2 (6h)
1. Add `tenacity` retry decorator to adapters
2. Standardize error handling
3. Add rate limiter

### Sprint 3 (4h)
1. Split server.py into modules
2. Improve test coverage to 90%

## Monitoring Debt

- [ ] No metrics/observability
- [ ] No logging structured
- [ ] No health checks

Recommend adding:
- OpenTelemetry traces
- Prometheus metrics
- Structured JSON logging
