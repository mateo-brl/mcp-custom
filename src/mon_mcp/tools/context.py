"""
Module de gestion du contexte de session.

Stocke des variables cle-valeur en memoire entre les appels d'outils.
Peut persister en JSON sur disque.

Outils: definir_contexte, obtenir_contexte, supprimer_contexte, sauvegarder_contexte
"""

import json
import os
import sys

# Limite de taille totale du contexte (10 MB)
MAX_CONTEXT_SIZE = 10 * 1024 * 1024

# Stockage en memoire
_context: dict = {}


def _context_size() -> int:
    """Estime la taille memoire du contexte."""
    return len(json.dumps(_context, ensure_ascii=False))


def definir_contexte(cle: str, valeur: str) -> str:
    """
    Stocke une variable dans le contexte de session.

    Args:
        cle: Nom de la variable (ex: "compteur", "resultats", "url_source")
        valeur: Valeur a stocker (texte ou JSON)

    Returns:
        Confirmation avec la cle et la valeur precedente si existante.
    """
    if not cle or not cle.strip():
        return json.dumps({"erreur": "La cle ne peut pas etre vide."}, ensure_ascii=False)

    cle = cle.strip()

    # Verifier la taille
    taille_ajout = len(cle) + len(valeur)
    if _context_size() + taille_ajout > MAX_CONTEXT_SIZE:
        return json.dumps({
            "erreur": "Limite de taille du contexte atteinte (10 MB). Supprimez des variables.",
        }, ensure_ascii=False)

    precedente = _context.get(cle)
    _context[cle] = valeur

    result = {
        "cle": cle,
        "valeur": valeur[:200] + "..." if len(valeur) > 200 else valeur,
        "total_variables": len(_context),
    }
    if precedente is not None:
        result["precedente_valeur"] = precedente[:200] + "..." if len(str(precedente)) > 200 else precedente

    return json.dumps(result, ensure_ascii=False)


def obtenir_contexte(cle: str = "") -> str:
    """
    Lit une variable ou tout le contexte de session.

    Args:
        cle: Nom de la variable a lire (vide = tout le contexte)

    Returns:
        JSON avec la valeur ou tout le contexte.
    """
    if not cle or not cle.strip():
        # Retourner tout le contexte
        if not _context:
            return json.dumps({"contexte": {}, "total": 0, "info": "Contexte vide."}, ensure_ascii=False)

        # Tronquer les valeurs longues pour l'affichage
        apercu = {}
        for k, v in _context.items():
            v_str = str(v)
            apercu[k] = v_str[:500] + "..." if len(v_str) > 500 else v_str

        return json.dumps({
            "contexte": apercu,
            "total": len(_context),
        }, ensure_ascii=False)

    cle = cle.strip()
    if cle not in _context:
        return json.dumps({"erreur": f"Variable '{cle}' non trouvee dans le contexte."}, ensure_ascii=False)

    return json.dumps({
        "cle": cle,
        "valeur": _context[cle],
    }, ensure_ascii=False)


def supprimer_contexte(cle: str) -> str:
    """
    Supprime une variable du contexte de session.

    Args:
        cle: Nom de la variable a supprimer

    Returns:
        Confirmation de la suppression.
    """
    cle = cle.strip()
    if cle not in _context:
        return json.dumps({"erreur": f"Variable '{cle}' non trouvee."}, ensure_ascii=False)

    valeur = _context.pop(cle)
    return json.dumps({
        "supprime": cle,
        "valeur_supprimee": str(valeur)[:200],
        "total_variables": len(_context),
    }, ensure_ascii=False)


def sauvegarder_contexte(fichier: str = "") -> str:
    """
    Persiste le contexte de session dans un fichier JSON.

    Args:
        fichier: Chemin du fichier JSON (defaut: .context.json dans le workspace ou repertoire courant)

    Returns:
        Confirmation avec le chemin du fichier et le nombre de variables sauvegardees.
    """
    if not fichier:
        # Essayer d'utiliser le workspace s'il est defini
        try:
            from mon_mcp.tools.workspace import _current_workspace
            if _current_workspace and os.path.isdir(_current_workspace):
                fichier = os.path.join(_current_workspace, ".context.json")
            else:
                fichier = os.path.join(os.getcwd(), ".context.json")
        except ImportError:
            fichier = os.path.join(os.getcwd(), ".context.json")

    fichier = os.path.abspath(fichier)

    if not _context:
        return json.dumps({"info": "Contexte vide, rien a sauvegarder."}, ensure_ascii=False)

    try:
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(_context, f, ensure_ascii=False, indent=2)

        taille = os.path.getsize(fichier)
        return json.dumps({
            "fichier": fichier,
            "variables": len(_context),
            "taille": f"{taille / 1024:.1f} KB" if taille > 1024 else f"{taille} B",
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"erreur": str(e)}, ensure_ascii=False)


def register_tools(mcp):
    mcp.add_tool(definir_contexte)
    mcp.add_tool(obtenir_contexte)
    mcp.add_tool(supprimer_contexte)
    mcp.add_tool(sauvegarder_contexte)
