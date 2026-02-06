"""Outils MCP pour la gestion du presse-papier Windows."""

import ctypes
import json


# Constantes Windows
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def lire_presse_papier() -> str:
    """
    Lit le texte du presse-papier.

    Returns:
        Le contenu texte du presse-papier.
    """
    try:
        if not user32.OpenClipboard(0):
            return "Erreur: impossible d'ouvrir le presse-papier"
        try:
            if not user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                return "Presse-papier vide ou ne contient pas de texte"

            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                return "Presse-papier vide"

            kernel32.GlobalLock.restype = ctypes.c_wchar_p
            text = kernel32.GlobalLock(handle)
            result = str(text) if text else ""
            kernel32.GlobalUnlock(handle)

            return json.dumps({"contenu": result}, ensure_ascii=False)
        finally:
            user32.CloseClipboard()
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
        if not user32.OpenClipboard(0):
            return "Erreur: impossible d'ouvrir le presse-papier"
        try:
            user32.EmptyClipboard()

            # Encoder en UTF-16-LE + null terminator
            encoded = texte.encode("utf-16-le") + b"\x00\x00"
            h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
            if not h_mem:
                return "Erreur: allocation memoire echouee"

            kernel32.GlobalLock.restype = ctypes.c_void_p
            ptr = kernel32.GlobalLock(h_mem)
            ctypes.memmove(ptr, encoded, len(encoded))
            kernel32.GlobalUnlock(h_mem)

            user32.SetClipboardData(CF_UNICODETEXT, h_mem)
            return f"Texte copie dans le presse-papier ({len(texte)} caracteres)"
        finally:
            user32.CloseClipboard()
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils presse-papier sur l'instance MCP."""
    mcp.add_tool(lire_presse_papier)
    mcp.add_tool(ecrire_presse_papier)
