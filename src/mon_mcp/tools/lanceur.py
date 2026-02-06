"""Outils MCP pour lancer des applications et ouvrir des URLs."""

import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path


def lancer_app(nom_ou_chemin: str) -> str:
    """
    Lance une application par nom ou chemin.

    Args:
        nom_ou_chemin: Nom de l'application (ex: "notepad", "firefox") ou chemin complet

    Returns:
        Confirmation du lancement ou message d'erreur.
    """
    try:
        path = Path(nom_ou_chemin)

        # Si c'est un chemin complet qui existe, le lancer directement
        if path.is_absolute() and path.exists():
            if sys.platform == "win32":
                import os
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
            return f"Application lancee: '{nom_ou_chemin}'"

        # Sinon, chercher l'executable par nom
        resolved = shutil.which(nom_ou_chemin)
        if resolved:
            subprocess.Popen([resolved])
            return f"Application lancee: '{nom_ou_chemin}' ({resolved})"

        # Dernier recours: tenter le lancement via le shell
        if sys.platform == "win32":
            import os
            try:
                os.startfile(nom_ou_chemin)
                return f"Application lancee: '{nom_ou_chemin}'"
            except OSError:
                pass
        else:
            try:
                subprocess.Popen(["xdg-open", nom_ou_chemin])
                return f"Application lancee: '{nom_ou_chemin}'"
            except FileNotFoundError:
                pass

        return f"Erreur: application '{nom_ou_chemin}' introuvable"
    except Exception as e:
        return f"Erreur: {str(e)}"


def ouvrir_url(url: str) -> str:
    """
    Ouvre une URL dans le navigateur par defaut.

    Args:
        url: L'URL a ouvrir (ex: "https://google.com")

    Returns:
        Confirmation.
    """
    try:
        if not url.startswith(("http://", "https://", "file://")):
            url = "https://" + url

        webbrowser.open(url)
        return f"URL ouverte dans le navigateur: {url}"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils lanceur sur l'instance MCP."""
    mcp.add_tool(lancer_app)
    mcp.add_tool(ouvrir_url)
