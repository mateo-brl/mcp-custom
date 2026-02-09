"""Tests pour le serveur MCP Custom."""

from mon_mcp.server import ping, mcp


def test_ping():
    """Test de la fonction ping."""
    result = ping()
    assert "pong" in result
    assert "MCP OK" in result


def test_all_tools_registered():
    """Verifie que tous les 58 outils sont enregistres."""
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
        # Lanceur
        "lancer_app", "ouvrir_url",
        # Recherche
        "rechercher_fichiers",
        # OCR
        "ocr_image", "ocr_ecran",
        # Excel/CSV
        "lire_excel", "ecrire_excel", "lire_csv", "ecrire_csv", "info_excel",
        # Execution
        "executer_commande", "executer_python", "executer_script",
        "verifier_commande", "lister_environnement",
        # Workspace
        "definir_workspace", "obtenir_workspace", "lister_workspace",
        "nettoyer_workspace", "archiver_workspace",
        # Web
        "telecharger_url", "extraire_texte_url", "verifier_url", "extraire_liens",
        # Documents
        "creer_word", "creer_powerpoint", "creer_pdf",
        # Context
        "definir_contexte", "obtenir_contexte", "supprimer_contexte", "sauvegarder_contexte",
    ]
    for name in expected:
        assert name in tools, f"Outil manquant: {name}"
    assert len(tools) == 58
