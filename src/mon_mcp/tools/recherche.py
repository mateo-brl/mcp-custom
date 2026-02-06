"""Outil MCP pour la recherche intelligente de fichiers."""

import fnmatch
import json
import os
from datetime import datetime
from pathlib import Path

MAX_SEARCH_SIZE = 10 * 1024 * 1024  # 10 MB max pour la recherche de contenu


def _format_size(size_bytes: int) -> str:
    """Formate une taille en octets en format lisible."""
    for unit in ["o", "Ko", "Mo", "Go", "To"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} Po"


def rechercher_fichiers(
    dossier: str,
    motif: str = "*",
    contenu: str = "",
    extensions: str = "",
    max_resultats: int = 50,
) -> str:
    """
    Recherche des fichiers par nom et/ou contenu.

    Args:
        dossier: Repertoire de recherche
        motif: Pattern de nom de fichier (ex: "*.py", "rapport*") (defaut: "*")
        contenu: Texte a chercher dans le contenu des fichiers (optionnel)
        extensions: Extensions filtrees, separees par virgules (ex: ".py,.txt") (optionnel)
        max_resultats: Nombre max de resultats (defaut: 50)

    Returns:
        Liste des fichiers trouves avec chemin, taille, date de modification.
    """
    try:
        base_path = Path(dossier)
        if not base_path.exists():
            return f"Erreur: le repertoire '{dossier}' n'existe pas"
        if not base_path.is_dir():
            return f"Erreur: '{dossier}' n'est pas un repertoire"

        # Parser les extensions
        ext_filter = set()
        if extensions:
            for ext in extensions.split(","):
                ext = ext.strip().lower()
                if not ext.startswith("."):
                    ext = "." + ext
                ext_filter.add(ext)

        resultats = []
        contenu_lower = contenu.lower() if contenu else ""

        for dirpath, dirnames, filenames in os.walk(dossier):
            # Ignorer les dossiers caches et speciaux
            dirnames[:] = [d for d in dirnames if not d.startswith((".", "__"))]

            for filename in filenames:
                if len(resultats) >= max_resultats:
                    break

                # Filtre par motif de nom
                if not fnmatch.fnmatch(filename.lower(), motif.lower()):
                    continue

                # Filtre par extension
                if ext_filter:
                    file_ext = Path(filename).suffix.lower()
                    if file_ext not in ext_filter:
                        continue

                filepath = os.path.join(dirpath, filename)

                try:
                    stat = os.stat(filepath)
                except (PermissionError, OSError):
                    continue

                # Filtre par contenu
                ligne_trouvee = None
                if contenu_lower:
                    if stat.st_size > MAX_SEARCH_SIZE:
                        continue
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if contenu_lower in line.lower():
                                    ligne_trouvee = i
                                    break
                            else:
                                continue  # Contenu non trouve, passer au fichier suivant
                    except (PermissionError, OSError, UnicodeDecodeError):
                        continue

                resultats.append({
                    "chemin": filepath,
                    "nom": filename,
                    "taille": _format_size(stat.st_size),
                    "modifie": datetime.fromtimestamp(stat.st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "ligne_trouvee": ligne_trouvee,
                })

            if len(resultats) >= max_resultats:
                break

        return json.dumps(
            {
                "dossier": str(base_path.resolve()),
                "motif": motif,
                "contenu_recherche": contenu or None,
                "nombre_resultats": len(resultats),
                "limite_atteinte": len(resultats) >= max_resultats,
                "resultats": resultats,
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils recherche sur l'instance MCP."""
    mcp.add_tool(rechercher_fichiers)
