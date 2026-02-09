"""
Module de gestion de workspace (dossier de travail).

Outils: definir_workspace, obtenir_workspace, lister_workspace,
        nettoyer_workspace, archiver_workspace
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

# Chemins proteges (repris de fichiers.py)
if sys.platform == "win32":
    _PROTECTED_PATHS = {
        "C:\\Windows", "C:\\Windows\\System32", "C:\\Program Files",
        "C:\\Program Files (x86)", "C:\\ProgramData",
    }
else:
    _PROTECTED_PATHS = {
        "/", "/bin", "/sbin", "/usr", "/etc", "/lib", "/lib64",
        "/boot", "/dev", "/proc", "/sys", "/var", "/root",
    }

# Etat du workspace courant
_current_workspace: str | None = None
_session_files: list[str] = []


def _is_protected(chemin: str) -> bool:
    """Verifie si un chemin est un repertoire systeme protege."""
    normalized = os.path.normpath(os.path.abspath(chemin))
    for protected in _PROTECTED_PATHS:
        if normalized == os.path.normpath(protected):
            return True
    return False


def _get_dir_info(path: str) -> dict:
    """Calcule les stats d'un repertoire."""
    total_size = 0
    file_count = 0
    dir_count = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                file_count += 1
                total_size += entry.stat(follow_symlinks=False).st_size
            elif entry.is_dir(follow_symlinks=False):
                dir_count += 1
    except PermissionError:
        pass

    if total_size < 1024:
        taille_str = f"{total_size} B"
    elif total_size < 1024 * 1024:
        taille_str = f"{total_size / 1024:.1f} KB"
    elif total_size < 1024 * 1024 * 1024:
        taille_str = f"{total_size / (1024 * 1024):.1f} MB"
    else:
        taille_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"

    return {
        "fichiers": file_count,
        "dossiers": dir_count,
        "taille_totale": taille_str,
        "taille_octets": total_size,
    }


def definir_workspace(chemin: str, creer_si_absent: bool = True) -> str:
    """
    Definit le dossier de travail actif (workspace).

    Args:
        chemin: Chemin absolu du dossier de travail
        creer_si_absent: Creer le dossier s'il n'existe pas (defaut: True)

    Returns:
        Confirmation avec info du workspace.
    """
    global _current_workspace, _session_files

    chemin = os.path.abspath(chemin)

    if _is_protected(chemin):
        return json.dumps({"erreur": f"Chemin systeme protege: {chemin}"}, ensure_ascii=False)

    cree = False
    if not os.path.exists(chemin):
        if creer_si_absent:
            os.makedirs(chemin, exist_ok=True)
            cree = True
        else:
            return json.dumps({"erreur": f"Repertoire inexistant: {chemin}"}, ensure_ascii=False)

    if not os.path.isdir(chemin):
        return json.dumps({"erreur": f"Le chemin n'est pas un repertoire: {chemin}"}, ensure_ascii=False)

    _current_workspace = chemin
    _session_files = []

    info = _get_dir_info(chemin)
    return json.dumps({
        "workspace": chemin,
        "cree": cree,
        **info,
    }, ensure_ascii=False)


def obtenir_workspace() -> str:
    """
    Retourne les informations du workspace actif.

    Returns:
        JSON avec chemin, nombre de fichiers, taille totale, etc.
    """
    if not _current_workspace:
        return json.dumps({"erreur": "Aucun workspace defini. Utilisez definir_workspace() d'abord."}, ensure_ascii=False)

    if not os.path.isdir(_current_workspace):
        return json.dumps({"erreur": f"Le workspace n'existe plus: {_current_workspace}"}, ensure_ascii=False)

    info = _get_dir_info(_current_workspace)
    return json.dumps({
        "workspace": _current_workspace,
        "actif": True,
        **info,
        "fichiers_session": len(_session_files),
    }, ensure_ascii=False)


def lister_workspace(pattern: str = "*", recursif: bool = False) -> str:
    """
    Liste les fichiers du workspace.

    Args:
        pattern: Pattern glob pour filtrer (ex: "*.py", "rapport*")
        recursif: Chercher recursivement dans les sous-dossiers

    Returns:
        JSON avec la liste des fichiers et leurs metadonnees.
    """
    if not _current_workspace:
        return json.dumps({"erreur": "Aucun workspace defini. Utilisez definir_workspace() d'abord."}, ensure_ascii=False)

    if not os.path.isdir(_current_workspace):
        return json.dumps({"erreur": f"Le workspace n'existe plus: {_current_workspace}"}, ensure_ascii=False)

    fichiers = []
    max_results = 200

    if recursif:
        for root, dirs, files in os.walk(_current_workspace):
            # Ignorer les dossiers caches
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if fnmatch(f, pattern):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, _current_workspace)
                    try:
                        stat = os.stat(full_path)
                        fichiers.append({
                            "nom": f,
                            "chemin_relatif": rel_path,
                            "taille": stat.st_size,
                            "modifie": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        })
                    except OSError:
                        continue
                    if len(fichiers) >= max_results:
                        break
            if len(fichiers) >= max_results:
                break
    else:
        try:
            for entry in os.scandir(_current_workspace):
                if entry.is_file() and fnmatch(entry.name, pattern):
                    stat = entry.stat()
                    fichiers.append({
                        "nom": entry.name,
                        "chemin_relatif": entry.name,
                        "taille": stat.st_size,
                        "modifie": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    })
                    if len(fichiers) >= max_results:
                        break
        except PermissionError:
            return json.dumps({"erreur": f"Permission refusee: {_current_workspace}"}, ensure_ascii=False)

    return json.dumps({
        "workspace": _current_workspace,
        "pattern": pattern,
        "recursif": recursif,
        "fichiers": fichiers,
        "total": len(fichiers),
        "limite_atteinte": len(fichiers) >= max_results,
    }, ensure_ascii=False)


def nettoyer_workspace(confirmer: bool = False) -> str:
    """
    Nettoie le workspace (supprime les fichiers temporaires).

    Args:
        confirmer: Si False, mode dry-run (montre ce qui serait supprime). Si True, supprime.

    Returns:
        JSON avec la liste des fichiers supprimes ou a supprimer.
    """
    if not _current_workspace:
        return json.dumps({"erreur": "Aucun workspace defini."}, ensure_ascii=False)

    if not os.path.isdir(_current_workspace):
        return json.dumps({"erreur": f"Le workspace n'existe plus: {_current_workspace}"}, ensure_ascii=False)

    # Patterns de fichiers temporaires
    temp_patterns = ["*.tmp", "*.temp", "*.bak", "*.swp", "*.log", "~*", "*.pyc"]
    temp_dirs = ["__pycache__", ".pytest_cache", "*.egg-info"]

    a_supprimer = []
    taille_totale = 0

    for entry in os.scandir(_current_workspace):
        if entry.is_file():
            if any(fnmatch(entry.name, pat) for pat in temp_patterns):
                stat = entry.stat()
                a_supprimer.append({
                    "nom": entry.name,
                    "type": "fichier",
                    "taille": stat.st_size,
                })
                taille_totale += stat.st_size
        elif entry.is_dir():
            if any(fnmatch(entry.name, pat) for pat in temp_dirs):
                a_supprimer.append({
                    "nom": entry.name,
                    "type": "dossier",
                })

    if confirmer and a_supprimer:
        supprimes = 0
        for item in a_supprimer:
            full_path = os.path.join(_current_workspace, item["nom"])
            try:
                if item["type"] == "fichier":
                    os.remove(full_path)
                else:
                    shutil.rmtree(full_path)
                supprimes += 1
            except OSError:
                continue

        return json.dumps({
            "action": "supprime",
            "supprimes": supprimes,
            "taille_liberee": taille_totale,
        }, ensure_ascii=False)

    return json.dumps({
        "action": "dry-run",
        "a_supprimer": a_supprimer,
        "total": len(a_supprimer),
        "taille_a_liberer": taille_totale,
        "info": "Relancez avec confirmer=True pour supprimer.",
    }, ensure_ascii=False)


def archiver_workspace(destination: str) -> str:
    """
    Cree une archive .zip du workspace.

    Args:
        destination: Chemin du fichier .zip a creer

    Returns:
        Confirmation avec nombre de fichiers archives et taille.
    """
    if not _current_workspace:
        return json.dumps({"erreur": "Aucun workspace defini."}, ensure_ascii=False)

    if not os.path.isdir(_current_workspace):
        return json.dumps({"erreur": f"Le workspace n'existe plus: {_current_workspace}"}, ensure_ascii=False)

    destination = os.path.abspath(destination)
    if not destination.endswith(".zip"):
        destination += ".zip"

    # Creer le dossier parent si necessaire
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    fichiers_archives = 0
    try:
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(_current_workspace):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for f in files:
                    full_path = os.path.join(root, f)
                    arcname = os.path.relpath(full_path, _current_workspace)
                    try:
                        zf.write(full_path, arcname)
                        fichiers_archives += 1
                    except (OSError, PermissionError):
                        continue

        taille = os.path.getsize(destination)
        if taille < 1024:
            taille_str = f"{taille} B"
        elif taille < 1024 * 1024:
            taille_str = f"{taille / 1024:.1f} KB"
        else:
            taille_str = f"{taille / (1024 * 1024):.1f} MB"

        return json.dumps({
            "archive": destination,
            "fichiers_archives": fichiers_archives,
            "taille_compresse": taille_str,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"erreur": str(e)}, ensure_ascii=False)


def register_tools(mcp):
    mcp.add_tool(definir_workspace)
    mcp.add_tool(obtenir_workspace)
    mcp.add_tool(lister_workspace)
    mcp.add_tool(nettoyer_workspace)
    mcp.add_tool(archiver_workspace)
