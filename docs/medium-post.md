# MCP Argentina: Datos económicos para tu AI

Un servidor MCP que conecta Claude, Cursor y otros AI con cotizaciones del dólar, inflación y riesgo país de Argentina.

## Qué incluye

- Dólar: Blue, Oficial, MEP, CCL, Cripto, Tarjeta, Mayorista
- Históricos de cotizaciones (30+ días)
- Inflación mensual, interanual y acumulada
- Riesgo país
- Monedas extranjeras (EUR, BRL, UYU, CLP)
- Conversiones ARS ↔ USD

## Instalación

```bash
pip install mcp-argentina
```

## Configuración

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

**Cursor** (`.cursor/mcp.json`):

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

## Ejemplo

> ¿Cuánto está el dólar blue?

```
Dólar Blue: $1,395 / $1,415
```

> ¿Cuál es la inflación?

```
Inflación: 2.9% mensual, 33.0% interanual
```

## Fuentes

- [dolarapi.com](https://dolarapi.com)
- [argentinadatos.com](https://argentinadatos.com)

## Links

- GitHub: https://github.com/greydina/mcp-argentina
- PyPI: https://pypi.org/project/mcp-argentina/
- Skill: https://github.com/greydina/skill-mcp-argentina

---

También lo tengo corriendo en WhatsApp con [OpenClaw](https://openclaw.ai) — en otro post explico [cómo armé comentarios de fútbol en vivo](https://medium.com/@jasinjunior/how-to-build-football-live-comments-using-openclaw-reddit-and-whatsapp-ad6acd67496d) usando la misma infraestructura.

Si te interesa recibir alertas de cotizaciones por WhatsApp, dejá un comentario.
