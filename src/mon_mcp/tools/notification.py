"""Outil MCP pour les notifications desktop."""

from mon_mcp.platform_api import send_notification as _send_notification


def notification(titre: str, message: str, duree: str = "short") -> str:
    """
    Envoie une notification desktop (toast).

    Args:
        titre: Titre de la notification
        message: Corps du message
        duree: "short" (~5 sec) ou "long" (~25 sec) (defaut: "short")

    Returns:
        Confirmation.
    """
    try:
        _send_notification(titre, message, duree)
        return f"Notification envoyee: '{titre}'"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils notification sur l'instance MCP."""
    mcp.add_tool(notification)
