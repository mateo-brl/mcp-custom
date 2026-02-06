"""Tests pour les outils systeme."""

from mon_mcp.tools.systeme import tuer_processus


def test_tuer_processus_refuse_critique():
    """Test que les processus critiques sont refuses."""
    result = tuer_processus("csrss.exe")
    assert "protege" in result.lower() or "refuse" in result.lower()


def test_tuer_processus_refuse_explorer():
    """Test que explorer.exe est refuse."""
    result = tuer_processus("explorer.exe")
    assert "protege" in result.lower() or "refuse" in result.lower()


def test_tuer_processus_pid_inexistant():
    """Test terminaison d'un PID qui n'existe pas."""
    result = tuer_processus("9999999")
    assert "aucun processus" in result.lower() or "erreur" in result.lower()
