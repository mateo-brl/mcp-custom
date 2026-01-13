"""Tests pour le serveur MCP custom."""

from mon_mcp.server import ping


def test_ping():
    """Test de la fonction ping."""
    result = ping()
    assert "pong" in result
    assert "MCP OK" in result
