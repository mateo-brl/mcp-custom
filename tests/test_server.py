"""Tests pour le serveur MCP custom."""

import pytest
from mon_mcp.server import saluer, calculer


def test_saluer():
    """Test de l'outil saluer."""
    result = saluer("Matéo")
    assert "Matéo" in result
    assert "Bonjour" in result


def test_calculer_addition():
    """Test de l'addition."""
    result = calculer("add", 5, 3)
    assert "8" in result


def test_calculer_soustraction():
    """Test de la soustraction."""
    result = calculer("sub", 10, 3)
    assert "7" in result


def test_calculer_multiplication():
    """Test de la multiplication."""
    result = calculer("mul", 4, 5)
    assert "20" in result


def test_calculer_division():
    """Test de la division."""
    result = calculer("div", 10, 2)
    assert "5" in result


def test_calculer_division_par_zero():
    """Test de la division par zéro."""
    result = calculer("div", 10, 0)
    assert "Erreur" in result or "zéro" in result


def test_calculer_operation_inconnue():
    """Test d'une opération non supportée."""
    result = calculer("pow", 2, 3)
    assert "inconnue" in result.lower() or "Utilise" in result
