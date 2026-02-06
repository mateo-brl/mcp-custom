"""
Serveur MCP Custom - Agent d'assistance visuelle.

Ce serveur permet de :
- Verifier que le MCP fonctionne (ping)
- Capturer les ecrans de l'ordinateur (+ region specifique)
- Lister et gerer les fenetres ouvertes
- Interagir avec l'ordinateur (clic, frappe clavier, scroll)
- Gerer des fichiers (lire, ecrire, copier, deplacer, supprimer)
- Surveiller le systeme (processus, CPU, RAM, disque)
- Envoyer des notifications Windows
- Lire/ecrire le presse-papier

Windows uniquement pour le moment.
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

capture.register_tools(mcp)
clavier.register_tools(mcp)
souris.register_tools(mcp)
fenetres.register_tools(mcp)
fichiers.register_tools(mcp)
systeme.register_tools(mcp)
notification.register_tools(mcp)
clipboard.register_tools(mcp)


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
    missing = []

    for module, name in [
        ("mss", "mss"),
        ("PIL", "Pillow"),
        ("pygetwindow", "pygetwindow"),
        ("psutil", "psutil"),
        ("winotify", "winotify"),
    ]:
        if importlib.util.find_spec(module) is None:
            missing.append(name)

    if missing:
        return (
            f"pong (MCP OK) - Dependances manquantes: {', '.join(missing)}. "
            f"Installez avec: pip install {' '.join(missing)}"
        )
    return "pong (MCP OK - Toutes les dependances sont installees)"


# =============================================================================
# POINT D'ENTREE
# =============================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
