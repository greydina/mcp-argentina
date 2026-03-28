"""Prompts MCP - templates de prompts para análisis económicos."""

from typing import Any


def get_analisis_economico_prompt() -> dict[str, Any]:
    """
    Prompt: analisis_economico
    
    Template para realizar un análisis completo de la situación económica argentina
    basado en cotizaciones y datos disponibles.
    
    Returns:
        Definición del prompt con placeholders y estructura.
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
- Contexto temporal

**Enfoque:** {enfoque}

**Tu análisis debe incluir:**
1. **Situación actual del mercado cambiario**
   - Cotizaciones principales (blue, oficial)
   - Brecha entre dólar blue y oficial
   - Significado económico de la brecha

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
    
    Template para comparar diferentes tipos de cambio y explicar sus diferencias.
    
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
   - Marco regulatorio

2. **Cotización actual**
   - Precio de compra y venta
   - Última actualización
   - Brecha con otros tipos

3. **Cuándo conviene usarlo**
   - Ventajas y desventajas
   - Casos de uso típicos
   - Requisitos o limitaciones

4. **Comparación relativa**
   - Diferencias de precio entre los tipos consultados
   - Por qué existen esas diferencias
   - Qué implican esas brechas

**Formato:** Tabla comparativa seguida de análisis.
**Tono:** Educativo, accesible para no especialistas.
**Incluir:** Ejemplos prácticos.
""",
    }


# Registry de prompts disponibles
AVAILABLE_PROMPTS = {
    "analisis_economico": get_analisis_economico_prompt,
    "comparar_dolares": get_comparar_dolares_prompt,
}


def get_prompt(name: str) -> dict[str, Any]:
    """
    Obtiene un prompt por nombre.
    
    Args:
        name: Nombre del prompt
        
    Returns:
        Definición del prompt
        
    Raises:
        KeyError: Si el prompt no existe
    """
    if name not in AVAILABLE_PROMPTS:
        raise KeyError(f"Prompt '{name}' no encontrado. Disponibles: {list(AVAILABLE_PROMPTS.keys())}")
    
    return AVAILABLE_PROMPTS[name]()


def list_prompts() -> list[dict[str, str]]:
    """
    Lista todos los prompts disponibles.
    
    Returns:
        Lista de prompts con nombre y descripción.
    """
    return [
        {
            "name": name,
            "description": func()["description"],
        }
        for name, func in AVAILABLE_PROMPTS.items()
    ]
