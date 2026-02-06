"""Outils MCP pour la reconnaissance optique de caracteres (OCR)."""

import json
from pathlib import Path


def ocr_image(chemin_image: str, langue: str = "fra+eng") -> str:
    """
    Extrait le texte d'une image via OCR.

    Args:
        chemin_image: Chemin vers le fichier image (png, jpg, bmp, tiff)
        langue: Langue(s) Tesseract (defaut: "fra+eng")

    Returns:
        Le texte extrait ou un message d'erreur.
    """
    try:
        import pytesseract
    except ImportError:
        return "Erreur: pytesseract non installe. pip install pytesseract"

    try:
        from PIL import Image
    except ImportError:
        return "Erreur: Pillow non installe. pip install Pillow"

    try:
        path = Path(chemin_image)
        if not path.exists():
            return f"Erreur: le fichier '{chemin_image}' n'existe pas"
        if not path.is_file():
            return f"Erreur: '{chemin_image}' n'est pas un fichier"

        supported = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif", ".webp"}
        if path.suffix.lower() not in supported:
            return f"Erreur: format non supporte '{path.suffix}'. Formats: {', '.join(supported)}"

        img = Image.open(chemin_image)
        texte = pytesseract.image_to_string(img, lang=langue)
        texte = texte.strip()

        return json.dumps(
            {
                "fichier": str(path.resolve()),
                "langue": langue,
                "texte": texte,
                "longueur": len(texte),
                "lignes": texte.count("\n") + 1 if texte else 0,
            },
            ensure_ascii=False,
            indent=2,
        )
    except pytesseract.TesseractNotFoundError:
        return (
            "Erreur: Tesseract n'est pas installe ou pas dans le PATH. "
            "Windows: https://github.com/UB-Mannheim/tesseract/wiki | "
            "Linux: sudo apt install tesseract-ocr tesseract-ocr-fra"
        )
    except Exception as e:
        return f"Erreur: {str(e)}"


def ocr_ecran(x: int, y: int, largeur: int, hauteur: int, langue: str = "fra+eng") -> str:
    """
    Capture une region de l'ecran et extrait le texte via OCR.

    Args:
        x: Position X du coin superieur gauche
        y: Position Y du coin superieur gauche
        largeur: Largeur de la region en pixels
        hauteur: Hauteur de la region en pixels
        langue: Langue(s) Tesseract (defaut: "fra+eng")

    Returns:
        Le texte extrait de la region capturee.
    """
    try:
        import pytesseract
    except ImportError:
        return "Erreur: pytesseract non installe. pip install pytesseract"

    try:
        import mss
        from PIL import Image
    except ImportError:
        return "Erreur: mss et Pillow requis. pip install mss Pillow"

    if largeur <= 0 or hauteur <= 0:
        return "Erreur: largeur et hauteur doivent etre positifs"

    try:
        monitor = {"left": x, "top": y, "width": largeur, "height": hauteur}

        with mss.mss() as sct:
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        texte = pytesseract.image_to_string(img, lang=langue)
        texte = texte.strip()

        return json.dumps(
            {
                "region": f"({x}, {y}) {largeur}x{hauteur}",
                "langue": langue,
                "texte": texte,
                "longueur": len(texte),
                "lignes": texte.count("\n") + 1 if texte else 0,
            },
            ensure_ascii=False,
            indent=2,
        )
    except pytesseract.TesseractNotFoundError:
        return (
            "Erreur: Tesseract n'est pas installe ou pas dans le PATH. "
            "Windows: https://github.com/UB-Mannheim/tesseract/wiki | "
            "Linux: sudo apt install tesseract-ocr tesseract-ocr-fra"
        )
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils OCR sur l'instance MCP."""
    mcp.add_tool(ocr_image)
    mcp.add_tool(ocr_ecran)
