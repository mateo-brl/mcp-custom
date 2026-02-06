"""Outils MCP pour le controle de la souris."""

import time

from mon_mcp.platform_api import (
    get_cursor_pos,
    set_cursor_pos,
    mouse_click,
    mouse_scroll,
)


def clic_souris(x: int, y: int, bouton: str = "left") -> str:
    """
    Effectue un clic de souris a une position donnee.

    Args:
        x: Position X sur l'ecran
        y: Position Y sur l'ecran
        bouton: "left", "right" ou "middle" (defaut: "left")

    Returns:
        Confirmation du clic.
    """
    try:
        mouse_click(x, y, bouton)
        return f"Clic {bouton} effectue a ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


def double_clic(x: int, y: int) -> str:
    """
    Effectue un double-clic a une position donnee.

    Args:
        x: Position X sur l'ecran
        y: Position Y sur l'ecran

    Returns:
        Confirmation du double-clic.
    """
    try:
        set_cursor_pos(x, y)
        mouse_click(x, y, "left")
        time.sleep(0.05)
        mouse_click(x, y, "left")
        return f"Double-clic effectue a ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


def position_souris() -> str:
    """
    Retourne la position actuelle de la souris.

    Returns:
        Les coordonnees X, Y de la souris.
    """
    try:
        x, y = get_cursor_pos()
        return f"Position actuelle: ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


def deplacer_souris(x: int, y: int, duree: float = 0.5) -> str:
    """
    Deplace la souris vers une position donnee avec mouvement fluide.

    Args:
        x: Position X cible
        y: Position Y cible
        duree: Duree du deplacement en secondes (defaut: 0.5, 0 = instantane)

    Returns:
        Confirmation.
    """
    try:
        if duree <= 0:
            set_cursor_pos(x, y)
        else:
            start_x, start_y = get_cursor_pos()
            steps = max(int(duree / 0.01), 1)
            for i in range(1, steps + 1):
                t = i / steps
                cur_x = int(start_x + (x - start_x) * t)
                cur_y = int(start_y + (y - start_y) * t)
                set_cursor_pos(cur_x, cur_y)
                time.sleep(duree / steps)
        return f"Souris deplacee vers ({x}, {y})"
    except Exception as e:
        return f"Erreur: {str(e)}"


def scroll(direction: str = "down", clicks: int = 3) -> str:
    """
    Effectue un scroll (defilement) a la position actuelle de la souris.

    Args:
        direction: "up" ou "down" (defaut: "down")
        clicks: Nombre de "clics" de scroll (defaut: 3)

    Returns:
        Confirmation.
    """
    try:
        amount = clicks if direction == "up" else -clicks
        mouse_scroll(amount)
        return f"Scroll {direction} de {clicks} clics"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils souris sur l'instance MCP."""
    mcp.add_tool(clic_souris)
    mcp.add_tool(double_clic)
    mcp.add_tool(position_souris)
    mcp.add_tool(deplacer_souris)
    mcp.add_tool(scroll)
