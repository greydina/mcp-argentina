"""Tests para MCP Server."""

import pytest
from mcp_argentina.infrastructure.mcp.server import (
    server,
    list_tools,
    list_resources,
    list_prompts,
    get_container,
)
from mcp_argentina.infrastructure.container import Container


class TestMCPServerTools:
    """Tests para tools del MCP server."""

    def setup_method(self) -> None:
        """Reset container antes de cada test."""
        Container.reset()

    @pytest.mark.asyncio
    async def test_list_tools_retorna_lista(self) -> None:
        """Debe retornar lista de tools."""
        tools = await list_tools()
        assert isinstance(tools, list)
        assert len(tools) >= 3

    @pytest.mark.asyncio
    async def test_list_tools_incluye_get_dolar(self) -> None:
        """Debe incluir tool get_dolar."""
        tools = await list_tools()
        names = [t.name for t in tools]
        assert "get_dolar" in names

    @pytest.mark.asyncio
    async def test_list_tools_incluye_get_cotizaciones(self) -> None:
        """Debe incluir tool get_cotizaciones."""
        tools = await list_tools()
        names = [t.name for t in tools]
        assert "get_cotizaciones" in names

    @pytest.mark.asyncio
    async def test_list_tools_incluye_convertir(self) -> None:
        """Debe incluir tool convertir."""
        tools = await list_tools()
        names = [t.name for t in tools]
        assert "convertir" in names

    @pytest.mark.asyncio
    async def test_list_tools_incluye_riesgo_pais(self) -> None:
        """Debe incluir tool get_riesgo_pais."""
        tools = await list_tools()
        names = [t.name for t in tools]
        assert "get_riesgo_pais" in names

    @pytest.mark.asyncio
    async def test_get_dolar_tiene_schema(self) -> None:
        """get_dolar debe tener input schema."""
        tools = await list_tools()
        get_dolar = next(t for t in tools if t.name == "get_dolar")
        assert "properties" in get_dolar.inputSchema
        assert "tipo" in get_dolar.inputSchema["properties"]


class TestMCPServerResources:
    """Tests para resources del MCP server."""

    @pytest.mark.asyncio
    async def test_list_resources_retorna_lista(self) -> None:
        """Debe retornar lista de resources."""
        resources = await list_resources()
        assert isinstance(resources, list)
        assert len(resources) >= 2

    @pytest.mark.asyncio
    async def test_list_resources_incluye_cotizaciones(self) -> None:
        """Debe incluir resource de cotizaciones."""
        resources = await list_resources()
        uris = [str(r.uri) for r in resources]
        assert any("cotizaciones" in uri for uri in uris)

    @pytest.mark.asyncio
    async def test_list_resources_incluye_indicadores(self) -> None:
        """Debe incluir resource de indicadores."""
        resources = await list_resources()
        uris = [str(r.uri) for r in resources]
        assert any("indicadores" in uri for uri in uris)


class TestMCPServerPrompts:
    """Tests para prompts del MCP server."""

    @pytest.mark.asyncio
    async def test_list_prompts_retorna_lista(self) -> None:
        """Debe retornar lista de prompts."""
        prompts = await list_prompts()
        assert isinstance(prompts, list)
        assert len(prompts) >= 2

    @pytest.mark.asyncio
    async def test_list_prompts_incluye_analisis(self) -> None:
        """Debe incluir prompt de análisis."""
        prompts = await list_prompts()
        names = [p.name for p in prompts]
        assert "analisis_economico" in names

    @pytest.mark.asyncio
    async def test_list_prompts_incluye_comparar(self) -> None:
        """Debe incluir prompt de comparación."""
        prompts = await list_prompts()
        names = [p.name for p in prompts]
        assert "comparar_dolares" in names


class TestMCPServerContainer:
    """Tests para container del server."""

    def setup_method(self) -> None:
        """Reset container antes de cada test."""
        Container.reset()

    def test_get_container_retorna_container(self) -> None:
        """Debe retornar instancia de Container."""
        container = get_container()
        assert isinstance(container, Container)

    def test_get_container_es_singleton(self) -> None:
        """Debe retornar la misma instancia."""
        c1 = get_container()
        c2 = get_container()
        assert c1 is c2
