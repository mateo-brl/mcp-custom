"""Tests pour le serveur MCP custom."""

import pytest
from mon_mcp.server import saluer, calculer


@pytest.mark.asyncio
async def test_saluer():
    """Test de l'outil saluer."""
    result = await saluer("Matéo")
    assert "Matéo" in result
    assert "Bonjour" in result


@pytest.mark.asyncio
async def test_calculer_addition():
    """Test de l'addition."""
    result = await calculer("add", 5, 3)
    assert "8" in result


@pytest.mark.asyncio
async def test_calculer_division():
    """Test de la division."""
    result = await calculer("div", 10, 2)
    assert "5" in result


@pytest.mark.asyncio
async def test_calculer_division_par_zero():
    """Test de la division par zéro."""
    result = await calculer("div", 10, 0)
    assert "Erreur" in result or "zéro" in result


@pytest.mark.asyncio
async def test_calculer_operation_inconnue():
    """Test d'une opération non supportée."""
    result = await calculer("pow", 2, 3)
    assert "inconnue" in result.lower() or "Utilise" in result
