"""Tests pour le module context."""

import json
import os
import tempfile

from mon_mcp.tools.context import (
    definir_contexte,
    obtenir_contexte,
    supprimer_contexte,
    sauvegarder_contexte,
    _context,
)


def setup_function():
    """Nettoyer le contexte avant chaque test."""
    _context.clear()


def test_definir_contexte():
    """Test ajout d'une variable."""
    result = json.loads(definir_contexte("nom", "Claude"))
    assert result["cle"] == "nom"
    assert result["total_variables"] == 1


def test_obtenir_contexte_cle():
    """Test lecture d'une variable specifique."""
    definir_contexte("x", "42")
    result = json.loads(obtenir_contexte("x"))
    assert result["valeur"] == "42"


def test_obtenir_contexte_tout():
    """Test lecture de tout le contexte."""
    definir_contexte("a", "1")
    definir_contexte("b", "2")
    result = json.loads(obtenir_contexte())
    assert result["total"] == 2
    assert "a" in result["contexte"]
    assert "b" in result["contexte"]


def test_obtenir_contexte_vide():
    """Test lecture contexte vide."""
    result = json.loads(obtenir_contexte())
    assert result["total"] == 0


def test_supprimer_contexte():
    """Test suppression d'une variable."""
    definir_contexte("temp", "value")
    result = json.loads(supprimer_contexte("temp"))
    assert result["supprime"] == "temp"
    assert result["total_variables"] == 0


def test_supprimer_contexte_inexistant():
    """Test suppression variable inexistante."""
    result = json.loads(supprimer_contexte("xyz"))
    assert "erreur" in result


def test_sauvegarder_contexte():
    """Test persistence en JSON."""
    definir_contexte("key1", "val1")
    definir_contexte("key2", "val2")
    with tempfile.TemporaryDirectory() as tmpdir:
        fichier = os.path.join(tmpdir, "ctx.json")
        result = json.loads(sauvegarder_contexte(fichier))
        assert result["variables"] == 2
        assert os.path.exists(fichier)
        # Verifier le contenu
        with open(fichier) as f:
            data = json.load(f)
        assert data["key1"] == "val1"
        assert data["key2"] == "val2"


def test_definir_contexte_remplacement():
    """Test remplacement d'une variable existante."""
    definir_contexte("counter", "1")
    result = json.loads(definir_contexte("counter", "2"))
    assert "precedente_valeur" in result
    assert result["precedente_valeur"] == "1"
