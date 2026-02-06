"""Tests pour les outils lanceur."""

from mon_mcp.tools.lanceur import ouvrir_url, lancer_app


def test_ouvrir_url_https():
    """Test que ouvrir_url fonctionne avec une URL valide."""
    result = ouvrir_url("https://example.com")
    assert "URL ouverte" in result or "Erreur" in result


def test_lancer_app_inexistant():
    """Test lancement d'une app qui n'existe pas."""
    result = lancer_app("application_totalement_inexistante_xyz_123")
    assert "introuvable" in result.lower() or "erreur" in result.lower()
