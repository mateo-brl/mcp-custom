"""
Serveur MCP Custom - Agent d'assistance visuelle.

Ce serveur permet de :
- Vérifier que le MCP fonctionne (ping)
- Capturer les écrans de l'ordinateur
- Lister les fenêtres ouvertes
- Interagir avec l'ordinateur (clic, frappe clavier)

⚠️ Windows uniquement pour le moment.
"""

import base64
import io
import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Création du serveur MCP
mcp = FastMCP("mon-mcp-custom")


# =============================================================================
# UTILITAIRES
# =============================================================================

def _check_dependencies():
    """Vérifie que les dépendances sont installées."""
    missing = []
    try:
        import mss
    except ImportError:
        missing.append("mss")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    try:
        import pyautogui
    except ImportError:
        missing.append("pyautogui")
    try:
        import pygetwindow
    except ImportError:
        missing.append("pygetwindow")
    
    return missing


# =============================================================================
# OUTILS MCP
# =============================================================================

@mcp.tool()
def ping() -> str:
    """
    Vérifie que le serveur MCP fonctionne correctement.
    
    Returns:
        "pong" si le serveur fonctionne, avec la liste des dépendances manquantes si applicable.
    """
    missing = _check_dependencies()
    if missing:
        return f"pong ✓ (MCP OK) - ⚠️ Dépendances manquantes pour les fonctions avancées: {', '.join(missing)}. Installez-les avec: pip install {' '.join(missing)}"
    return "pong ✓ (MCP OK - Toutes les dépendances sont installées)"


@mcp.tool()
def capture_ecrans() -> str:
    """
    Capture tous les écrans de l'ordinateur.
    
    Returns:
        Une description des écrans capturés avec les images en base64.
    """
    try:
        import mss
        from PIL import Image
    except ImportError as e:
        return f"Erreur: dépendance manquante ({e}). Installez avec: pip install mss Pillow"
    
    try:
        with mss.mss() as sct:
            monitors = sct.monitors
            result = {
                "nombre_ecrans": len(monitors) - 1,  # -1 car le premier est l'écran virtuel combiné
                "ecrans": []
            }
            
            # Capturer chaque écran (on skip le monitor[0] qui est l'écran virtuel combiné)
            for i, monitor in enumerate(monitors[1:], 1):
                screenshot = sct.grab(monitor)
                
                # Convertir en PNG base64
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Réduire la taille pour ne pas surcharger (max 1920x1080)
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
            
            # Retourner un résumé + les images
            summary = f"✓ {result['nombre_ecrans']} écran(s) capturé(s):\n"
            for ecran in result["ecrans"]:
                summary += f"  - Écran {ecran['ecran']}: {ecran['resolution']} à {ecran['position']}\n"
            
            return json.dumps(result, ensure_ascii=False)
            
    except Exception as e:
        return f"Erreur lors de la capture: {str(e)}"


@mcp.tool()
def capture_ecran_principal() -> str:
    """
    Capture uniquement l'écran principal.
    
    Returns:
        L'image de l'écran principal en base64.
    """
    try:
        import mss
        from PIL import Image
    except ImportError as e:
        return f"Erreur: dépendance manquante ({e}). Installez avec: pip install mss Pillow"
    
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Écran principal
            screenshot = sct.grab(monitor)
            
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Réduire la taille
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
    Liste toutes les fenêtres ouvertes sur l'ordinateur.
    
    Returns:
        La liste des fenêtres avec leur titre et position.
    """
    try:
        import pygetwindow as gw
    except ImportError:
        return "Erreur: pygetwindow non installé. Installez avec: pip install pygetwindow"
    
    try:
        windows = gw.getAllWindows()
        result = []
        
        for win in windows:
            if win.title:  # Ignorer les fenêtres sans titre
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
    Met le focus sur une fenêtre spécifique.
    
    Args:
        titre: Le titre (ou partie du titre) de la fenêtre à activer.
        
    Returns:
        Confirmation ou erreur.
    """
    try:
        import pygetwindow as gw
    except ImportError:
        return "Erreur: pygetwindow non installé. Installez avec: pip install pygetwindow"
    
    try:
        windows = gw.getWindowsWithTitle(titre)
        if not windows:
            return f"Aucune fenêtre trouvée avec le titre contenant: '{titre}'"
        
        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        
        return f"✓ Fenêtre '{win.title}' activée"
        
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def clic_souris(x: int, y: int, bouton: str = "left") -> str:
    """
    Effectue un clic de souris à une position donnée.
    
    Args:
        x: Position X sur l'écran
        y: Position Y sur l'écran
        bouton: "left", "right" ou "middle" (défaut: "left")
        
    Returns:
        Confirmation du clic.
    """
    try:
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installé. Installez avec: pip install pyautogui"
    
    try:
        pyautogui.click(x, y, button=bouton)
        return f"✓ Clic {bouton} effectué à ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def double_clic(x: int, y: int) -> str:
    """
    Effectue un double-clic à une position donnée.
    
    Args:
        x: Position X sur l'écran
        y: Position Y sur l'écran
        
    Returns:
        Confirmation du double-clic.
    """
    try:
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installé. Installez avec: pip install pyautogui"
    
    try:
        pyautogui.doubleClick(x, y)
        return f"✓ Double-clic effectué à ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def ecrire_texte(texte: str, intervalle: float = 0.05) -> str:
    """
    Écrit du texte au clavier (simule la frappe).
    
    Args:
        texte: Le texte à écrire
        intervalle: Délai entre chaque caractère en secondes (défaut: 0.05)
        
    Returns:
        Confirmation.
    """
    try:
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installé. Installez avec: pip install pyautogui"
    
    try:
        pyautogui.typewrite(texte, interval=intervalle)
        return f"✓ Texte écrit: '{texte}'"
    except Exception as e:
        # Pour les caractères spéciaux/unicode, utiliser write
        try:
            pyautogui.write(texte)
            return f"✓ Texte écrit: '{texte}'"
        except Exception as e2:
            return f"Erreur: {str(e2)}"


@mcp.tool()
def touche_clavier(touche: str) -> str:
    """
    Appuie sur une touche spéciale du clavier.
    
    Args:
        touche: La touche à presser (ex: "enter", "tab", "escape", "backspace", "ctrl+c", "alt+f4")
        
    Returns:
        Confirmation.
    """
    try:
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installé. Installez avec: pip install pyautogui"
    
    try:
        if "+" in touche:
            # Combinaison de touches (ex: ctrl+c)
            keys = touche.lower().split("+")
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(touche)
        return f"✓ Touche '{touche}' pressée"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def position_souris() -> str:
    """
    Retourne la position actuelle de la souris.
    
    Returns:
        Les coordonnées X, Y de la souris.
    """
    try:
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installé. Installez avec: pip install pyautogui"
    
    try:
        x, y = pyautogui.position()
        return f"Position actuelle: ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def deplacer_souris(x: int, y: int, duree: float = 0.5) -> str:
    """
    Déplace la souris vers une position donnée.
    
    Args:
        x: Position X cible
        y: Position Y cible
        duree: Durée du déplacement en secondes (défaut: 0.5)
        
    Returns:
        Confirmation.
    """
    try:
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installé. Installez avec: pip install pyautogui"
    
    try:
        pyautogui.moveTo(x, y, duration=duree)
        return f"✓ Souris déplacée vers ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


@mcp.tool()
def scroll(direction: str = "down", clicks: int = 3) -> str:
    """
    Effectue un scroll (défilement) à la position actuelle de la souris.
    
    Args:
        direction: "up" ou "down" (défaut: "down")
        clicks: Nombre de "clics" de scroll (défaut: 3)
        
    Returns:
        Confirmation.
    """
    try:
        import pyautogui
    except ImportError:
        return "Erreur: pyautogui non installé. Installez avec: pip install pyautogui"
    
    try:
        amount = clicks if direction == "up" else -clicks
        pyautogui.scroll(amount)
        return f"✓ Scroll {direction} de {clicks} clics"
    except Exception as e:
        return f"Erreur: {str(e)}"


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
