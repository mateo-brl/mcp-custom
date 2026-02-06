"""Outils MCP pour le controle du clavier."""

from mon_mcp.platform_api import type_text as _type_text, press_key as _press_key


def ecrire_texte(texte: str, intervalle: float = 0.05) -> str:
    """
    Ecrit du texte au clavier (simule la frappe).
    Supporte tous les caracteres Unicode (majuscules, accents, symboles).

    Args:
        texte: Le texte a ecrire
        intervalle: Delai entre chaque caractere en secondes (defaut: 0.05)

    Returns:
        Confirmation.
    """
    try:
        _type_text(texte, intervalle)
        return f"Texte ecrit: '{texte}'"
    except Exception as e:
        return f"Erreur: {str(e)}"


def touche_clavier(touche: str) -> str:
    """
    Appuie sur une touche speciale du clavier.

    Args:
        touche: La touche a presser (ex: "enter", "tab", "escape", "backspace", "ctrl+c", "alt+f4")

    Returns:
        Confirmation.
    """
    try:
        _press_key(touche)
        return f"Touche '{touche}' pressee"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils clavier sur l'instance MCP."""
    mcp.add_tool(ecrire_texte)
    mcp.add_tool(touche_clavier)
