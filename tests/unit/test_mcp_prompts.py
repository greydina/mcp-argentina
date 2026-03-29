"""Tests para MCP prompts."""

from mcp_argentina.infrastructure.mcp.prompts import (
    get_analisis_economico_prompt,
    get_comparar_dolares_prompt,
)


class TestPromptAnalisisEconomico:
    """Tests para prompt de análisis económico."""

    def test_retorna_diccionario(self) -> None:
        """Debe retornar un diccionario."""
        result = get_analisis_economico_prompt()
        assert isinstance(result, dict)

    def test_tiene_name(self) -> None:
        """Debe tener nombre."""
        result = get_analisis_economico_prompt()
        assert "name" in result
        assert result["name"] == "analisis_economico"

    def test_tiene_description(self) -> None:
        """Debe tener descripción."""
        result = get_analisis_economico_prompt()
        assert "description" in result
        assert len(result["description"]) > 0

    def test_tiene_template(self) -> None:
        """Debe tener template."""
        result = get_analisis_economico_prompt()
        assert "template" in result
        assert len(result["template"]) > 100

    def test_tiene_arguments(self) -> None:
        """Debe definir argumentos."""
        result = get_analisis_economico_prompt()
        assert "arguments" in result
        assert isinstance(result["arguments"], list)

    def test_template_menciona_dolar(self) -> None:
        """Template debe mencionar dólar."""
        result = get_analisis_economico_prompt()
        template_lower = result["template"].lower()
        assert "dólar" in template_lower or "dolar" in template_lower


class TestPromptCompararDolares:
    """Tests para prompt de comparación de dólares."""

    def test_retorna_diccionario(self) -> None:
        """Debe retornar un diccionario."""
        result = get_comparar_dolares_prompt()
        assert isinstance(result, dict)

    def test_tiene_name(self) -> None:
        """Debe tener nombre."""
        result = get_comparar_dolares_prompt()
        assert "name" in result
        assert result["name"] == "comparar_dolares"

    def test_tiene_description(self) -> None:
        """Debe tener descripción."""
        result = get_comparar_dolares_prompt()
        assert "description" in result
        assert len(result["description"]) > 0

    def test_tiene_template(self) -> None:
        """Debe tener template."""
        result = get_comparar_dolares_prompt()
        assert "template" in result
        assert len(result["template"]) > 50

    def test_template_tiene_placeholder_tipos(self) -> None:
        """Template debe tener placeholder para tipos."""
        result = get_comparar_dolares_prompt()
        template = result["template"]
        assert "{tipos}" in template


class TestPromptsCoherencia:
    """Tests de coherencia entre prompts."""

    def test_prompts_son_diferentes(self) -> None:
        """Cada prompt debe ser único."""
        analisis = get_analisis_economico_prompt()
        comparar = get_comparar_dolares_prompt()
        assert analisis["name"] != comparar["name"]
        assert analisis["template"] != comparar["template"]

    def test_prompts_tienen_estructura_consistente(self) -> None:
        """Ambos prompts deben tener la misma estructura."""
        analisis = get_analisis_economico_prompt()
        comparar = get_comparar_dolares_prompt()

        for prompt in [analisis, comparar]:
            assert "name" in prompt
            assert "description" in prompt
            assert "template" in prompt
