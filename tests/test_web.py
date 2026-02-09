"""Tests pour le module web."""

import json

from mon_mcp.tools.web import (
    verifier_url,
    extraire_texte_url,
    _validate_url,
)


def test_validate_url_https():
    """Test validation URL avec https."""
    assert _validate_url("https://example.com") == "https://example.com"


def test_validate_url_auto_https():
    """Test ajout automatique de https."""
    assert _validate_url("example.com") == "https://example.com"


def test_validate_url_vide():
    """Test URL vide."""
    assert _validate_url("") is None


def test_validate_url_http():
    """Test validation URL avec http."""
    assert _validate_url("http://example.com") == "http://example.com"


def test_verifier_url_invalide():
    """Test verification d'une URL invalide."""
    result = json.loads(verifier_url(""))
    assert "erreur" in result


def test_verifier_url_accessible():
    """Test verification d'une URL accessible (httpbin)."""
    result = json.loads(verifier_url("https://httpbin.org/status/200", timeout=10))
    assert result["accessible"] is True
    assert result["code_statut"] == 200


def test_extraire_texte_url_invalide():
    """Test extraction depuis URL invalide."""
    result = json.loads(extraire_texte_url(""))
    assert "erreur" in result
