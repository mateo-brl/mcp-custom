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
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Creation du serveur MCP
mcp = FastMCP("mon-mcp-custom")


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
    
    # On ne teste PAS pyautogui/pygetwindow ici car ils bloquent
    # On verifie juste si les modules existent
    import importlib.util
    if importlib.util.find_spec("pyautogui") is None:
        missing.append("pyautogui")
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
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installe. Installez avec: pip install pyautogui"

    try:
        pyautogui.click(x, y, button=bouton)
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
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installe. Installez avec: pip install pyautogui"

    try:
        pyautogui.doubleClick(x, y)
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
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installe. Installez avec: pip install pyautogui"

    try:
        pyautogui.typewrite(texte, interval=intervalle)
        return f"Texte ecrit: '{texte}'"
    except Exception as e:
        try:
            import pyautogui
            pyautogui.write(texte)
            return f"Texte ecrit: '{texte}'"
        except Exception as e2:
            return f"Erreur: {str(e2)}"


@mcp.tool()
def touche_clavier(touche: str) -> str:
    """
    Appuie sur une touche speciale du clavier.

    Args:
        touche: La touche a presser (ex: "enter", "tab", "escape", "backspace", "ctrl+c", "alt+f4")
        
    Returns:
        Confirmation.
    """
    try:
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installe. Installez avec: pip install pyautogui"

    try:
        if "+" in touche:
            keys = touche.lower().split("+")
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(touche)
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
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installe. Installez avec: pip install pyautogui"

    try:
        x, y = pyautogui.position()
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
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installe. Installez avec: pip install pyautogui"

    try:
        pyautogui.moveTo(x, y, duration=duree)
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
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installe. Installez avec: pip install pyautogui"

    try:
        amount = clicks if direction == "up" else -clicks
        pyautogui.scroll(amount)
        return f"Scroll {direction} de {clicks} clics"
    except Exception as e:
        return f"Erreur: {str(e)}"


# =============================================================================
# POINT D'ENTREE
# =============================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
