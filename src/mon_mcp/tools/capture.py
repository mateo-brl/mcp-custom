"""Outils MCP pour la capture d'ecran."""

import base64
import io
import json

from mon_mcp.win_api import get_virtual_screen_bounds


def _capture_region(monitor, max_size=None):
    """
    Helper: capture une region d'ecran et retourne (resolution, base64).

    Args:
        monitor: dict avec left, top, width, height
        max_size: tuple (w, h) max ou None pour taille originale
    """
    import mss
    from PIL import Image

    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        if max_size:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        resolution = f"{monitor['width']}x{monitor['height']}"
        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return resolution, img_b64


def capture_ecrans() -> str:
    """
    Capture tous les ecrans de l'ordinateur.

    Returns:
        Une description des ecrans captures avec les images en base64.
    """
    try:
        import mss
    except ImportError:
        return "Erreur: mss non installe. pip install mss Pillow"

    try:
        with mss.mss() as sct:
            monitors = sct.monitors
            result = {
                "nombre_ecrans": len(monitors) - 1,
                "ecrans": [],
            }
            for i, monitor in enumerate(monitors[1:], 1):
                resolution, img_b64 = _capture_region(monitor, max_size=(1920, 1080))
                result["ecrans"].append({
                    "ecran": i,
                    "resolution": resolution,
                    "position": f"({monitor['left']}, {monitor['top']})",
                    "image_base64": img_b64,
                })
            return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Erreur lors de la capture: {str(e)}"


def capture_ecran_principal() -> str:
    """
    Capture uniquement l'ecran principal.

    Returns:
        L'image de l'ecran principal en base64.
    """
    try:
        import mss
    except ImportError:
        return "Erreur: mss non installe. pip install mss Pillow"

    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            resolution, img_b64 = _capture_region(monitor, max_size=(1920, 1080))
            return json.dumps({
                "resolution": resolution,
                "image_base64": img_b64,
            })
    except Exception as e:
        return f"Erreur lors de la capture: {str(e)}"


def capture_region(x: int, y: int, largeur: int, hauteur: int) -> str:
    """
    Capture une region specifique de l'ecran.

    Args:
        x: Position X du coin superieur gauche
        y: Position Y du coin superieur gauche
        largeur: Largeur de la region en pixels
        hauteur: Hauteur de la region en pixels

    Returns:
        L'image de la region en base64.
    """
    try:
        import mss
    except ImportError:
        return "Erreur: mss non installe. pip install mss Pillow"

    if largeur <= 0 or hauteur <= 0:
        return "Erreur: largeur et hauteur doivent etre positifs"

    try:
        vx, vy, vw, vh = get_virtual_screen_bounds()
        if x < vx or y < vy or x + largeur > vx + vw or y + hauteur > vy + vh:
            return (
                f"Erreur: region ({x},{y},{largeur}x{hauteur}) depasse les limites "
                f"de l'ecran virtuel ({vx},{vy},{vw}x{vh})"
            )

        monitor = {"left": x, "top": y, "width": largeur, "height": hauteur}
        resolution, img_b64 = _capture_region(monitor)
        return json.dumps({
            "region": f"({x}, {y}) {largeur}x{hauteur}",
            "resolution": resolution,
            "image_base64": img_b64,
        })
    except Exception as e:
        return f"Erreur lors de la capture: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils de capture sur l'instance MCP."""
    mcp.add_tool(capture_ecrans)
    mcp.add_tool(capture_ecran_principal)
    mcp.add_tool(capture_region)
