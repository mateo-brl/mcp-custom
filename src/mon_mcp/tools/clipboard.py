"""Outils MCP pour la gestion du presse-papier."""

import json

from mon_mcp.platform_api import clipboard_read, clipboard_write


def lire_presse_papier() -> str:
    """
    Lit le texte du presse-papier.

    Returns:
        Le contenu texte du presse-papier.
    """
    try:
        text = clipboard_read()
        if not text:
            return "Presse-papier vide ou ne contient pas de texte"
        return json.dumps({"contenu": text}, ensure_ascii=False)
    except Exception as e:
        return f"Erreur: {str(e)}"


def ecrire_presse_papier(texte: str) -> str:
    """
    Ecrit du texte dans le presse-papier.

    Args:
        texte: Le texte a copier dans le presse-papier

    Returns:
        Confirmation.
    """
    try:
        clipboard_write(texte)
        return f"Texte copie dans le presse-papier ({len(texte)} caracteres)"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils presse-papier sur l'instance MCP."""
    mcp.add_tool(lire_presse_papier)
    mcp.add_tool(ecrire_presse_papier)
