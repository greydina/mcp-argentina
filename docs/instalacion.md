# 📦 Guía de Instalación

Esta guía cubre la instalación de MCP Argentina para diferentes casos de uso.

---

## Requisitos del Sistema

### Mínimos

- **Python:** 3.11 o superior
- **Sistema Operativo:** Linux, macOS, Windows
- **RAM:** 256 MB mínimo
- **Espacio en disco:** 50 MB

### Recomendados

- **Python:** 3.12+
- **RAM:** 512 MB
- **Conexión a internet:** Estable (para consultar APIs)

---

## Instalación Básica

### 1. Clonar el Repositorio

```bash
git clone https://github.com/anibaljasin/mcp-argentina.git
cd mcp-argentina
```

### 2. Crear Entorno Virtual

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

**Para uso normal:**
```bash
pip install -e .
```

**Para desarrollo (incluye testing, linting, etc.):**
```bash
pip install -e ".[dev]"
```

### 4. Verificar Instalación

```bash
python -c "from mcp_argentina import __version__; print(__version__)"
```

Deberías ver la versión instalada (ej: `0.1.0`).

---

## Configuración como Servidor MCP

### Para Claude Desktop

1. Abrir archivo de configuración:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. Agregar servidor:

```json
{
  "mcpServers": {
    "argentina": {
      "command": "python",
      "args": ["-m", "mcp_argentina.infrastructure.mcp.server"],
      "cwd": "/ruta/completa/a/mcp-argentina",
      "env": {}
    }
  }
}
```

3. Reiniciar Claude Desktop

4. Verificar que aparezca 🔌 en la interfaz indicando servidor conectado

### Para OpenClaw

Agregar a `openclaw.json`:

```json
{
  "mcpServers": {
    "argentina": {
      "command": "python",
      "args": ["-m", "mcp_argentina.infrastructure.mcp.server"],
      "cwd": "/home/user/mcp-argentina"
    }
  }
}
```

Reiniciar gateway:
```bash
openclaw gateway restart
```

### Para Cursor

Agregar a configuración de MCP en Cursor settings:

```json
{
  "mcp.servers": {
    "argentina": {
      "command": "python",
      "args": ["-m", "mcp_argentina.infrastructure.mcp.server"],
      "cwd": "/ruta/a/mcp-argentina"
    }
  }
}
```

---

## Instalación para Desarrollo

Si vas a contribuir al proyecto:

### 1. Fork y Clone

```bash
git clone https://github.com/TU_USUARIO/mcp-argentina.git
cd mcp-argentina
```

### 2. Instalar Dependencias de Desarrollo

```bash
pip install -e ".[dev]"
```

Esto instala:
- `pytest` — Testing
- `pytest-asyncio` — Tests async
- `pytest-cov` — Cobertura de tests
- `ruff` — Linting y formatting
- `mypy` — Type checking
- `pre-commit` — Git hooks

### 3. Configurar Pre-commit Hooks

```bash
pre-commit install
```

Esto ejecutará automáticamente linting y tests antes de cada commit.

### 4. Verificar Setup

```bash
# Ejecutar tests
pytest

# Verificar linting
ruff check .

# Verificar types
mypy mcp_argentina
```

Todo debería pasar sin errores.

---

## Solución de Problemas

### Error: `ModuleNotFoundError: No module named 'mcp_argentina'`

**Causa:** El paquete no está instalado o el entorno virtual no está activado.

**Solución:**
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar en modo editable
pip install -e .
```

### Error: `python: command not found`

**Causa:** Python no está en PATH o no está instalado.

**Solución:**
```bash
# Verificar Python instalado
python3 --version

# Usar python3 si python no funciona
python3 -m venv venv
```

### Error: Connection timeout al consultar APIs

**Causa:** Problemas de red o firewall bloqueando dolarapi.com.

**Solución:**
1. Verificar conectividad:
   ```bash
   curl https://dolarapi.com/v1/dolares/blue
   ```
2. Si tu red bloquea el acceso, configurar proxy o VPN

### MCP Server no aparece en Claude Desktop

**Posibles causas:**

1. **Path incorrecto:**
   ```json
   "cwd": "/ruta/absoluta/completa"  # Usar path absoluto
   ```

2. **Entorno virtual no configurado:**
   ```json
   "command": "/ruta/completa/venv/bin/python"  # Usar python del venv
   ```

3. **Logs de Claude Desktop:**
   - macOS: `~/Library/Logs/Claude/mcp*.log`
   - Windows: `%APPDATA%\Claude\logs\mcp*.log`

---

## Actualización

### Desde Git

```bash
cd mcp-argentina
git pull origin main
pip install -e ".[dev]"  # Reinstalar si hay nuevas dependencias
```

### Verificar Versión

```bash
python -c "from mcp_argentina import __version__; print(__version__)"
```

---

## Desinstalación

```bash
# Desactivar entorno virtual
deactivate

# Eliminar directorio
rm -rf mcp-argentina/

# Si instalaste globalmente
pip uninstall mcp-argentina
```

---

## Siguientes Pasos

- [Guía de Uso](uso.md) — Aprender a usar el servidor
- [Referencia de API](api.md) — Ver todos los tools disponibles
- [Guía de Desarrollo](desarrollo.md) — Contribuir al proyecto
