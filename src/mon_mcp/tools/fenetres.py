"""Outils MCP pour la gestion des fenetres."""

import json

from mon_mcp.platform_api import list_windows, focus_window as _focus_window


def liste_fenetres() -> str:
    """
    Liste toutes les fenetres ouvertes sur l'ordinateur.

    Returns:
        La liste des fenetres avec leur titre et position.
    """
    try:
        windows = list_windows()
        return json.dumps(windows, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Erreur: {str(e)}"


def focus_fenetre(titre: str) -> str:
    """
    Met le focus sur une fenetre specifique.

    Args:
        titre: Le titre (ou partie du titre) de la fenetre a activer.

    Returns:
        Confirmation ou erreur.
    """
    try:
        activated = _focus_window(titre)
        return f"Fenetre '{activated}' activee"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils fenetres sur l'instance MCP."""
    mcp.add_tool(liste_fenetres)
    mcp.add_tool(focus_fenetre)
