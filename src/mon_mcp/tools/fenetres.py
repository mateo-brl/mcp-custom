"""Outils MCP pour la gestion des fenetres Windows."""

import json


def liste_fenetres() -> str:
    """
    Liste toutes les fenetres ouvertes sur l'ordinateur.

    Returns:
        La liste des fenetres avec leur titre et position.
    """
    try:
        import pygetwindow as gw
    except ImportError:
        return "Erreur: pygetwindow non installe. pip install pygetwindow"

    try:
        windows = gw.getAllWindows()
        result = []

        for win in windows:
            if win.title:
                result.append({
                    "titre": win.title,
                    "position": f"({win.left}, {win.top})",
                    "taille": f"{win.width}x{win.height}",
                    "visible": win.visible,
                    "minimisee": win.isMinimized,
                    "active": win.isActive,
                })

        return json.dumps(result, ensure_ascii=False, indent=2)
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
        import pygetwindow as gw
    except ImportError:
        return "Erreur: pygetwindow non installe. pip install pygetwindow"

    try:
        windows = gw.getWindowsWithTitle(titre)
        if not windows:
            return f"Aucune fenetre trouvee avec le titre contenant: '{titre}'"

        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()

        return f"Fenetre '{win.title}' activee"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils fenetres sur l'instance MCP."""
    mcp.add_tool(liste_fenetres)
    mcp.add_tool(focus_fenetre)
