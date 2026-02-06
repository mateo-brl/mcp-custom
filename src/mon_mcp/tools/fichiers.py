"""Outils MCP pour la gestion de fichiers."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# Chemins systeme proteges contre la suppression
PROTECTED_PATHS = {
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
    "C:\\ProgramData", "C:\\Users", "C:\\System Volume Information",
    "C:\\$Recycle.Bin", "C:\\Recovery",
}

MAX_READ_SIZE = 10 * 1024 * 1024  # 10 MB


def _is_protected_path(chemin: str) -> bool:
    """Verifie si un chemin est protege."""
    normalized = os.path.normpath(os.path.abspath(chemin))
    # Refuse les racines de lecteur (C:\, D:\, etc.)
    if len(normalized) <= 3:
        return True
    for protected in PROTECTED_PATHS:
        if normalized.lower() == protected.lower():
            return True
    return False


def _format_size(size_bytes: int) -> str:
    """Formate une taille en octets en format lisible."""
    for unit in ["o", "Ko", "Mo", "Go", "To"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} Po"


def lire_fichier(chemin: str, encodage: str = "utf-8") -> str:
    """
    Lit le contenu d'un fichier texte.

    Args:
        chemin: Chemin du fichier a lire
        encodage: Encodage du fichier (defaut: utf-8)

    Returns:
        Le contenu du fichier ou un message d'erreur.
    """
    try:
        path = Path(chemin)
        if not path.exists():
            return f"Erreur: le fichier '{chemin}' n'existe pas"
        if not path.is_file():
            return f"Erreur: '{chemin}' n'est pas un fichier"

        size = path.stat().st_size
        if size > MAX_READ_SIZE:
            return (
                f"Erreur: le fichier fait {_format_size(size)} "
                f"(limite: {_format_size(MAX_READ_SIZE)})"
            )

        content = path.read_text(encoding=encodage)
        return json.dumps({
            "fichier": str(path.resolve()),
            "taille": _format_size(size),
            "lignes": content.count("\n") + 1,
            "contenu": content,
        }, ensure_ascii=False)
    except UnicodeDecodeError:
        return f"Erreur: impossible de lire '{chemin}' avec l'encodage {encodage} (fichier binaire ?)"
    except Exception as e:
        return f"Erreur: {str(e)}"


def ecrire_fichier(chemin: str, contenu: str, encodage: str = "utf-8") -> str:
    """
    Ecrit ou cree un fichier texte.

    Args:
        chemin: Chemin du fichier a creer/ecrire
        contenu: Contenu a ecrire
        encodage: Encodage du fichier (defaut: utf-8)

    Returns:
        Confirmation avec la taille du fichier.
    """
    try:
        path = Path(chemin)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contenu, encoding=encodage)
        size = path.stat().st_size
        return f"Fichier ecrit: '{path.resolve()}' ({_format_size(size)})"
    except Exception as e:
        return f"Erreur: {str(e)}"


def copier_fichier(source: str, destination: str) -> str:
    """
    Copie un fichier ou repertoire.

    Args:
        source: Chemin source
        destination: Chemin destination

    Returns:
        Confirmation de la copie.
    """
    try:
        src = Path(source)
        if not src.exists():
            return f"Erreur: '{source}' n'existe pas"

        if src.is_dir():
            shutil.copytree(source, destination)
            return f"Repertoire copie: '{source}' -> '{destination}'"
        else:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            return f"Fichier copie: '{source}' -> '{destination}'"
    except Exception as e:
        return f"Erreur: {str(e)}"


def deplacer_fichier(source: str, destination: str) -> str:
    """
    Deplace ou renomme un fichier ou repertoire.

    Args:
        source: Chemin source
        destination: Chemin destination

    Returns:
        Confirmation du deplacement.
    """
    try:
        if not Path(source).exists():
            return f"Erreur: '{source}' n'existe pas"

        Path(destination).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source, destination)
        return f"Deplace: '{source}' -> '{destination}'"
    except Exception as e:
        return f"Erreur: {str(e)}"


def supprimer_fichier(chemin: str) -> str:
    """
    Supprime un fichier ou repertoire.

    Args:
        chemin: Chemin du fichier ou repertoire a supprimer

    Returns:
        Confirmation de la suppression.
    """
    try:
        if _is_protected_path(chemin):
            return f"Refuse: '{chemin}' est un chemin systeme protege"

        path = Path(chemin)
        if not path.exists():
            return f"Erreur: '{chemin}' n'existe pas"

        if path.is_dir():
            count = sum(1 for _ in path.rglob("*"))
            shutil.rmtree(chemin)
            return f"Repertoire supprime: '{chemin}' ({count} elements)"
        else:
            os.remove(chemin)
            return f"Fichier supprime: '{chemin}'"
    except Exception as e:
        return f"Erreur: {str(e)}"


def lister_repertoire(chemin: str = ".") -> str:
    """
    Liste le contenu d'un repertoire avec details.

    Args:
        chemin: Chemin du repertoire (defaut: repertoire courant)

    Returns:
        La liste des fichiers et dossiers avec details.
    """
    try:
        path = Path(chemin)
        if not path.exists():
            return f"Erreur: '{chemin}' n'existe pas"
        if not path.is_dir():
            return f"Erreur: '{chemin}' n'est pas un repertoire"

        entries = []
        for entry in sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            try:
                stat = entry.stat()
                entries.append({
                    "nom": entry.name,
                    "type": "dossier" if entry.is_dir() else "fichier",
                    "taille": _format_size(stat.st_size) if entry.is_file() else "-",
                    "modifie": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })
            except (PermissionError, OSError):
                entries.append({
                    "nom": entry.name,
                    "type": "inconnu",
                    "taille": "-",
                    "modifie": "-",
                })

        return json.dumps({
            "repertoire": str(path.resolve()),
            "nombre_elements": len(entries),
            "contenu": entries,
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Erreur: {str(e)}"


def info_fichier(chemin: str) -> str:
    """
    Retourne les metadonnees d'un fichier ou repertoire.

    Args:
        chemin: Chemin du fichier ou repertoire

    Returns:
        Les metadonnees detaillees.
    """
    try:
        path = Path(chemin)
        if not path.exists():
            return f"Erreur: '{chemin}' n'existe pas"

        stat = path.stat()
        info = {
            "chemin": str(path.resolve()),
            "nom": path.name,
            "type": "dossier" if path.is_dir() else "fichier",
            "taille": _format_size(stat.st_size),
            "taille_octets": stat.st_size,
            "cree": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modifie": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "accede": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            "lecture_seule": not os.access(chemin, os.W_OK),
        }

        if path.is_file():
            info["extension"] = path.suffix or "(aucune)"

        if path.is_dir():
            try:
                items = list(path.iterdir())
                info["nb_fichiers"] = sum(1 for i in items if i.is_file())
                info["nb_dossiers"] = sum(1 for i in items if i.is_dir())
            except PermissionError:
                info["nb_fichiers"] = "acces refuse"

        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Erreur: {str(e)}"


def creer_repertoire(chemin: str) -> str:
    """
    Cree un repertoire (avec les parents si necessaire).

    Args:
        chemin: Chemin du repertoire a creer

    Returns:
        Confirmation de la creation.
    """
    try:
        path = Path(chemin)
        if path.exists():
            return f"Le repertoire '{chemin}' existe deja"

        path.mkdir(parents=True, exist_ok=True)
        return f"Repertoire cree: '{path.resolve()}'"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils fichiers sur l'instance MCP."""
    mcp.add_tool(lire_fichier)
    mcp.add_tool(ecrire_fichier)
    mcp.add_tool(copier_fichier)
    mcp.add_tool(deplacer_fichier)
    mcp.add_tool(supprimer_fichier)
    mcp.add_tool(lister_repertoire)
    mcp.add_tool(info_fichier)
    mcp.add_tool(creer_repertoire)
