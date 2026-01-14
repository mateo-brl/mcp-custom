"""
Serveur MCP Custom - Agent d'assistance visuelle.

Ce serveur permet de :
- Verifier que le MCP fonctionne (ping)
- Capturer les ecrans de l'ordinateur
- Lister les fenetres ouvertes
- Interagir avec l'ordinateur (clic, frappe clavier)

Windows uniquement pour le moment.
"""

import base64
import io
import json
import ctypes
from ctypes import wintypes
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Creation du serveur MCP
mcp = FastMCP("mon-mcp-custom")


# =============================================================================
# WINDOWS API (pour eviter pyautogui qui bloque)
# =============================================================================

user32 = ctypes.windll.user32

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def _get_cursor_pos():
    """Recupere la position de la souris via Windows API."""
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def _set_cursor_pos(x, y):
    """Deplace la souris via Windows API."""
    user32.SetCursorPos(x, y)


def _mouse_click(x, y, button="left"):
    """Effectue un clic via Windows API."""
    # Deplacer la souris
    user32.SetCursorPos(x, y)
    
    # Constantes pour les evenements souris
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_MIDDLEDOWN = 0x0020
    MOUSEEVENTF_MIDDLEUP = 0x0040
    
    if button == "left":
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif button == "right":
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    elif button == "middle":
        user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)


def _mouse_scroll(clicks):
    """Effectue un scroll via Windows API."""
    MOUSEEVENTF_WHEEL = 0x0800
    WHEEL_DELTA = 120
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, clicks * WHEEL_DELTA, 0)


# =============================================================================
# OUTILS MCP
# =============================================================================

@mcp.tool()
def ping() -> str:
    """
    Verifie que le serveur MCP fonctionne correctement.

    Returns:
        "pong" si le serveur fonctionne, avec la liste des dependances manquantes si applicable.
    """
    missing = []
    
    try:
        import mss
    except ImportError:
        missing.append("mss")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    
    import importlib.util
    if importlib.util.find_spec("pygetwindow") is None:
        missing.append("pygetwindow")
    
    if missing:
        return f"pong (MCP OK) - Dependances manquantes: {', '.join(missing)}. Installez avec: pip install {' '.join(missing)}"
    return "pong (MCP OK - Toutes les dependances sont installees)"


@mcp.tool()
def capture_ecrans() -> str:
    """
    Capture tous les ecrans de l'ordinateur.

    Returns:
        Une description des ecrans captures avec les images en base64.
    """
    try:
        import mss
        from PIL import Image
    except ImportError as e:
        return f"Erreur: dependance manquante ({e}). Installez avec: pip install mss Pillow"

    try:
        with mss.mss() as sct:
            monitors = sct.monitors
            result = {
                "nombre_ecrans": len(monitors) - 1,
                "ecrans": []
            }

            for i, monitor in enumerate(monitors[1:], 1):
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                max_size = (1920, 1080)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                buffer = io.BytesIO()
                img.save(buffer, format="PNG", optimize=True)
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

                result["ecrans"].append({
                    "ecran": i,
                    "resolution": f"{monitor['width']}x{monitor['height']}",
                    "position": f"({monitor['left']}, {monitor['top']})",
                    "image_base64": img_base64
                })

            return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return f"Erreur lors de la capture: {str(e)}"


@mcp.tool()
def capture_ecran_principal() -> str:
    """
    Capture uniquement l'ecran principal.

    Returns:
        L'image de l'ecran principal en base64.
    """
    try:
        import mss
        from PIL import Image
    except ImportError as e:
        return f"Erreur: dependance manquante ({e}). Installez avec: pip install mss Pillow"

    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            max_size = (1920, 1080)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            return json.dumps({
                "resolution": f"{monitor['width']}x{monitor['height']}",
                "image_base64": img_base64
            })

    except Exception as e:
        return f"Erreur lors de la capture: {str(e)}"


@mcp.tool()
def liste_fenetres() -> str:
    """
    Liste toutes les fenetres ouvertes sur l'ordinateur.

    Returns:
        La liste des fenetres avec leur titre et position.
    """
    try:
        import pygetwindow as gw
    except ImportError:
        return "Erreur: pygetwindow non installe. Installez avec: pip install pygetwindow"

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
                    "active": win.isActive
                })

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
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
        return "Erreur: pygetwindow non installe. Installez avec: pip install pygetwindow"

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


@mcp.tool()
def clic_souris(x: int, y: int, bouton: str = "left") -> str:
    """
    Effectue un clic de souris a une position donnee.

    Args:
        x: Position X sur l'ecran
        y: Position Y sur l'ecran
        bouton: "left", "right" ou "middle" (defaut: "left")
        
    Returns:
        Confirmation du clic.
    """
    try:
        _mouse_click(x, y, bouton)
        return f"Clic {bouton} effectue a ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def double_clic(x: int, y: int) -> str:
    """
    Effectue un double-clic a une position donnee.

    Args:
        x: Position X sur l'ecran
        y: Position Y sur l'ecran
        
    Returns:
        Confirmation du double-clic.
    """
    try:
        _mouse_click(x, y, "left")
        _mouse_click(x, y, "left")
        return f"Double-clic effectue a ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def ecrire_texte(texte: str, intervalle: float = 0.05) -> str:
    """
    Ecrit du texte au clavier (simule la frappe).

    Args:
        texte: Le texte a ecrire
        intervalle: Delai entre chaque caractere en secondes (defaut: 0.05)
        
    Returns:
        Confirmation.
    """
    try:
        import time
        for char in texte:
            # Utiliser SendInput pour chaque caractere
            if char.isascii():
                vk = ctypes.windll.user32.VkKeyScanW(ord(char))
                if vk != -1:
                    ctypes.windll.user32.keybd_event(vk & 0xFF, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(vk & 0xFF, 0, 2, 0)
            time.sleep(intervalle)
        return f"Texte ecrit: '{texte}'"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def touche_clavier(touche: str) -> str:
    """
    Appuie sur une touche speciale du clavier.

    Args:
        touche: La touche a presser (ex: "enter", "tab", "escape", "backspace", "ctrl+c", "alt+f4")
        
    Returns:
        Confirmation.
    """
    # Mapping des touches speciales vers les codes virtuels Windows
    VK_CODES = {
        "enter": 0x0D, "return": 0x0D,
        "tab": 0x09,
        "escape": 0x1B, "esc": 0x1B,
        "backspace": 0x08,
        "delete": 0x2E,
        "space": 0x20,
        "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
        "home": 0x24, "end": 0x23,
        "pageup": 0x21, "pagedown": 0x22,
        "ctrl": 0x11, "alt": 0x12, "shift": 0x10,
        "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
        "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
        "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
        "a": 0x41, "b": 0x42, "c": 0x43, "d": 0x44, "e": 0x45,
        "f": 0x46, "g": 0x47, "h": 0x48, "i": 0x49, "j": 0x4A,
        "k": 0x4B, "l": 0x4C, "m": 0x4D, "n": 0x4E, "o": 0x4F,
        "p": 0x50, "q": 0x51, "r": 0x52, "s": 0x53, "t": 0x54,
        "u": 0x55, "v": 0x56, "w": 0x57, "x": 0x58, "y": 0x59, "z": 0x5A,
    }
    
    try:
        if "+" in touche:
            # Combinaison de touches
            keys = [k.strip().lower() for k in touche.split("+")]
            # Appuyer sur les touches
            for key in keys:
                vk = VK_CODES.get(key)
                if vk:
                    user32.keybd_event(vk, 0, 0, 0)
            # Relacher dans l'ordre inverse
            for key in reversed(keys):
                vk = VK_CODES.get(key)
                if vk:
                    user32.keybd_event(vk, 0, 2, 0)
        else:
            vk = VK_CODES.get(touche.lower())
            if vk:
                user32.keybd_event(vk, 0, 0, 0)
                user32.keybd_event(vk, 0, 2, 0)
            else:
                return f"Touche inconnue: {touche}"
        
        return f"Touche '{touche}' pressee"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def position_souris() -> str:
    """
    Retourne la position actuelle de la souris.

    Returns:
        Les coordonnees X, Y de la souris.
    """
    try:
        x, y = _get_cursor_pos()
        return f"Position actuelle: ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def deplacer_souris(x: int, y: int, duree: float = 0.5) -> str:
    """
    Deplace la souris vers une position donnee.

    Args:
        x: Position X cible
        y: Position Y cible
        duree: Duree du deplacement en secondes (defaut: 0.5)
        
    Returns:
        Confirmation.
    """
    try:
        _set_cursor_pos(x, y)
        return f"Souris deplacee vers ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def scroll(direction: str = "down", clicks: int = 3) -> str:
    """
    Effectue un scroll (defilement) a la position actuelle de la souris.

    Args:
        direction: "up" ou "down" (defaut: "down")
        clicks: Nombre de "clics" de scroll (defaut: 3)
        
    Returns:
        Confirmation.
    """
    try:
        amount = clicks if direction == "up" else -clicks
        _mouse_scroll(amount)
        return f"Scroll {direction} de {clicks} clics"
    except Exception as e:
        return f"Erreur: {str(e)}"


# =============================================================================
# POINT D'ENTREE
# =============================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
