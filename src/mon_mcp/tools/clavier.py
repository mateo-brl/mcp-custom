"""Outils MCP pour le controle du clavier."""

import time

from mon_mcp.win_api import (
    VK_CODES,
    KEYEVENTF_KEYUP,
    send_input,
    make_key_input,
    make_unicode_input,
    user32,
)


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
        for char in texte:
            code = ord(char)
            down = make_unicode_input(code, key_up=False)
            up = make_unicode_input(code, key_up=True)
            send_input(down, up)
            time.sleep(intervalle)
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
        if "+" in touche:
            keys = [k.strip().lower() for k in touche.split("+")]
            for key in keys:
                vk = VK_CODES.get(key)
                if vk:
                    inp = make_key_input(vk=vk)
                    send_input(inp)
            for key in reversed(keys):
                vk = VK_CODES.get(key)
                if vk:
                    inp = make_key_input(vk=vk, flags=KEYEVENTF_KEYUP)
                    send_input(inp)
        else:
            vk = VK_CODES.get(touche.lower())
            if vk:
                down = make_key_input(vk=vk)
                up = make_key_input(vk=vk, flags=KEYEVENTF_KEYUP)
                send_input(down, up)
            else:
                return f"Touche inconnue: {touche}"

        return f"Touche '{touche}' pressee"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils clavier sur l'instance MCP."""
    mcp.add_tool(ecrire_texte)
    mcp.add_tool(touche_clavier)
