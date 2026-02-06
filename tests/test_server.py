"""Tests pour le serveur MCP Custom."""

from mon_mcp.server import ping, mcp


def test_ping():
    """Test de la fonction ping."""
    result = ping()
    assert "pong" in result
    assert "MCP OK" in result


def test_all_tools_registered():
    """Verifie que tous les 27 outils sont enregistres."""
    tools = list(mcp._tool_manager._tools.keys())
    expected = [
        "ping",
        # Capture
        "capture_ecrans", "capture_ecran_principal", "capture_region",
        # Souris
        "clic_souris", "double_clic", "position_souris", "deplacer_souris", "scroll",
        # Clavier
        "ecrire_texte", "touche_clavier",
        # Fenetres
        "liste_fenetres", "focus_fenetre",
        # Fichiers
        "lire_fichier", "ecrire_fichier", "copier_fichier", "deplacer_fichier",
        "supprimer_fichier", "lister_repertoire", "info_fichier", "creer_repertoire",
        # Systeme
        "liste_processus", "info_systeme", "tuer_processus",
        # Notification
        "notification",
        # Clipboard
        "lire_presse_papier", "ecrire_presse_papier",
    ]
    for name in expected:
        assert name in tools, f"Outil manquant: {name}"
    assert len(tools) == 27
