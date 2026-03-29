"""
Prompts MCP - Templates de prompts para análisis económicos.

Este módulo contiene los templates de prompts disponibles.
La implementación MCP real está en server.py.
"""

from typing import Any


def get_analisis_economico_prompt() -> dict[str, Any]:
    """
    Prompt: analisis_economico
    
    Template para realizar un análisis completo de la situación
    económica argentina basado en cotizaciones y datos disponibles.
    
    Returns:
        Definición del prompt con estructura y template.
    """
    return {
        "name": "analisis_economico",
        "description": "Genera un análisis de la situación económica argentina basado en cotizaciones actuales",
        "arguments": [
            {
                "name": "enfoque",
                "description": "Área de enfoque: 'general', 'mercado_cambiario', 'brecha', 'tendencias'",
                "required": False,
            }
        ],
        "template": """Analiza la situación económica argentina actual considerando:

**Datos disponibles:**
- Cotizaciones del dólar (blue, oficial, MEP, CCL)
- Brecha cambiaria
- Riesgo país
- Contexto temporal

**Enfoque:** {enfoque}

**Tu análisis debe incluir:**

1. **Situación actual del mercado cambiario**
   - Cotizaciones principales (blue, oficial)
   - Brecha entre dólar blue y oficial
   - Significado económico de la brecha actual

2. **Interpretación económica**
   - Qué indican las cotizaciones sobre la economía
   - Factores que pueden estar influyendo
   - Contexto histórico relevante

3. **Implicancias prácticas**
   - Para ahorristas
   - Para empresas que importan/exportan
   - Para el ciudadano promedio

4. **Recomendaciones generales**
   - Estrategias de cobertura cambiaria
   - Consideraciones para diferentes perfiles

**Formato:** Claro, conciso, en español argentino.
**Tono:** Informativo, sin sensacionalismo.
**Extensión:** 300-500 palabras.
""",
    }


def get_comparar_dolares_prompt() -> dict[str, Any]:
    """
    Prompt: comparar_dolares
    
    Template para comparar diferentes tipos de cambio
    y explicar sus diferencias y usos.
    
    Returns:
        Definición del prompt con estructura de comparación.
    """
    return {
        "name": "comparar_dolares",
        "description": "Compara diferentes tipos de dólar y explica sus diferencias y usos",
        "arguments": [
            {
                "name": "tipos",
                "description": "Lista de tipos de dólar a comparar (ej: 'blue,oficial,mep')",
                "required": True,
            }
        ],
        "template": """Compara los siguientes tipos de dólar en Argentina: {tipos}

Para cada tipo, explica:

1. **Definición y características**
   - Qué es este tipo de dólar
   - Cómo se opera/accede a él
   - Marco regulatorio (legal vs informal)

2. **Cotización actual**
   - Precio de compra y venta
   - Última actualización
   - Spread (diferencia compra-venta)

3. **Casos de uso**
   - Para qué tipo de operaciones se usa
   - Quiénes lo utilizan típicamente
   - Ventajas y desventajas

4. **Comparación directa**
   - Tabla comparativa de cotizaciones
   - Diferencias porcentuales entre tipos
   - Cuál conviene según el caso

**Recomendación final:**
Indica cuál tipo de dólar usar según:
- Ahorro personal
- Operaciones comerciales
- Viajes al exterior
- Inversiones

**Formato:** Estructurado con tablas donde corresponda.
**Idioma:** Español argentino.
""",
    }


# Constantes para compatibilidad con tests legacy
PROMPT_ANALISIS_ECONOMICO = get_analisis_economico_prompt()["template"]
PROMPT_COMPARAR_DOLARES = get_comparar_dolares_prompt()["template"]
