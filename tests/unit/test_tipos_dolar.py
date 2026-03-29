"""Tests para TipoDolar enum."""

import pytest

from mcp_argentina.domain.value_objects.tipos_dolar import TipoDolar


class TestTipoDolar:
    """Tests del enum TipoDolar."""

    def test_tipos_basicos_existen(self) -> None:
        """Deben existir los tipos básicos."""
        assert TipoDolar.OFICIAL is not None
        assert TipoDolar.BLUE is not None
        assert TipoDolar.MEP is not None
        assert TipoDolar.CCL is not None
        assert TipoDolar.CRIPTO is not None
        assert TipoDolar.TARJETA is not None

    def test_desde_string_valido(self) -> None:
        """Debe crear desde string válido."""
        assert TipoDolar.desde_string("blue") == TipoDolar.BLUE
        assert TipoDolar.desde_string("OFICIAL") == TipoDolar.OFICIAL
        assert TipoDolar.desde_string("Mep") == TipoDolar.MEP

    def test_desde_string_invalido_falla(self) -> None:
        """Debe fallar con string inválido."""
        with pytest.raises(ValueError):
            TipoDolar.desde_string("inexistente")

    def test_es_regulado(self) -> None:
        """Debe identificar tipos regulados."""
        assert TipoDolar.OFICIAL.es_regulado() is True
        assert TipoDolar.BLUE.es_regulado() is False
        assert TipoDolar.MEP.es_regulado() is False

    def test_es_paralelo(self) -> None:
        """Debe identificar tipos paralelos."""
        assert TipoDolar.BLUE.es_paralelo() is True
        assert TipoDolar.CRIPTO.es_paralelo() is True
        assert TipoDolar.OFICIAL.es_paralelo() is False

    def test_permite_compra_fisica(self) -> None:
        """Debe indicar si permite compra física."""
        assert TipoDolar.BLUE.permite_compra_fisica() is True
        assert TipoDolar.MEP.permite_compra_fisica() is False
        assert TipoDolar.CCL.permite_compra_fisica() is False

    def test_descripcion(self) -> None:
        """Debe tener descripción."""
        desc = TipoDolar.BLUE.descripcion()
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_list_devuelve_todos(self) -> None:
        """Debe poder listar todos los tipos."""
        todos = list(TipoDolar)
        assert len(todos) >= 6
        assert TipoDolar.BLUE in todos
        assert TipoDolar.OFICIAL in todos
