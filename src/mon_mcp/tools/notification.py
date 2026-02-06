"""Outil MCP pour les notifications Windows (toast)."""


def notification(titre: str, message: str, duree: str = "short") -> str:
    """
    Envoie une notification Windows (toast).

    Args:
        titre: Titre de la notification
        message: Corps du message
        duree: "short" (~5 sec) ou "long" (~25 sec) (defaut: "short")

    Returns:
        Confirmation.
    """
    try:
        from winotify import Notification, audio
    except ImportError:
        return "Erreur: winotify non installe. pip install winotify"

    try:
        toast = Notification(
            app_id="MCP Custom",
            title=titre,
            msg=message,
            duration=duree,
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
        return f"Notification envoyee: '{titre}'"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils notification sur l'instance MCP."""
    mcp.add_tool(notification)
