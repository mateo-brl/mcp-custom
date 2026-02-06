"""
Serveur MCP Custom - Agent d'assistance visuelle.

Ce serveur permet de :
- Verifier que le MCP fonctionne (ping)
- Capturer les ecrans de l'ordinateur (+ region specifique)
- Lister et gerer les fenetres ouvertes
- Interagir avec l'ordinateur (clic, frappe clavier, scroll)
- Gerer des fichiers (lire, ecrire, copier, deplacer, supprimer)
- Surveiller le systeme (processus, CPU, RAM, disque)
- Envoyer des notifications
- Lire/ecrire le presse-papier
- Lancer des applications et ouvrir des URLs
- Rechercher des fichiers par nom et contenu
- Extraire du texte par OCR
- Manipuler des fichiers Excel et CSV

Compatible Windows et Linux.
"""

import importlib.util

from mcp.server.fastmcp import FastMCP

# Creation du serveur MCP
mcp = FastMCP("mon-mcp-custom")


# =============================================================================
# ENREGISTREMENT DES MODULES D'OUTILS
# =============================================================================

from mon_mcp.tools import capture, clavier, souris, fenetres  # noqa: E402
from mon_mcp.tools import fichiers, systeme, notification, clipboard  # noqa: E402
from mon_mcp.tools import lanceur, recherche, ocr, excel  # noqa: E402

capture.register_tools(mcp)
clavier.register_tools(mcp)
souris.register_tools(mcp)
fenetres.register_tools(mcp)
fichiers.register_tools(mcp)
systeme.register_tools(mcp)
notification.register_tools(mcp)
clipboard.register_tools(mcp)
lanceur.register_tools(mcp)
recherche.register_tools(mcp)
ocr.register_tools(mcp)
excel.register_tools(mcp)


# =============================================================================
# OUTIL DIAGNOSTIC (meta-outil, reste dans server.py)
# =============================================================================

@mcp.tool()
def ping() -> str:
    """
    Verifie que le serveur MCP fonctionne correctement.

    Returns:
        "pong" si le serveur fonctionne, avec la liste des dependances manquantes si applicable.
    """
    import sys
    missing = []

    # Dependances cross-platform
    for module, name in [
        ("mss", "mss"),
        ("PIL", "Pillow"),
        ("psutil", "psutil"),
    ]:
        if importlib.util.find_spec(module) is None:
            missing.append(name)

    # Dependances specifiques a la plateforme
    if sys.platform == "win32":
        for module, name in [("pygetwindow", "pygetwindow"), ("winotify", "winotify")]:
            if importlib.util.find_spec(module) is None:
                missing.append(name)
    elif sys.platform == "linux":
        for module, name in [("pynput", "pynput"), ("pyperclip", "pyperclip"), ("notifypy", "notify-py")]:
            if importlib.util.find_spec(module) is None:
                missing.append(name)

    # Dependances optionnelles
    for module, name in [("pytesseract", "pytesseract"), ("openpyxl", "openpyxl")]:
        if importlib.util.find_spec(module) is None:
            missing.append(f"{name} (optionnel)")

    platform_name = {"win32": "Windows", "linux": "Linux"}.get(sys.platform, sys.platform)
    if missing:
        return (
            f"pong (MCP OK - {platform_name}) - Manquantes: {', '.join(missing)}"
        )
    return f"pong (MCP OK - {platform_name} - Toutes les dependances installees)"


# =============================================================================
# POINT D'ENTREE
# =============================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
