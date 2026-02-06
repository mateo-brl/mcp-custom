"""Stub pour les plateformes non supportees (macOS, etc.)."""


def _unsupported(name):
    """Cree une fonction qui leve NotImplementedError."""
    def fn(*args, **kwargs):
        raise NotImplementedError(
            f"'{name}' n'est pas disponible sur cette plateforme. "
            f"Plateformes supportees: Windows, Linux."
        )
    fn.__name__ = name
    fn.__doc__ = f"{name} - non disponible sur cette plateforme."
    return fn


get_cursor_pos = _unsupported("get_cursor_pos")
set_cursor_pos = _unsupported("set_cursor_pos")
mouse_click = _unsupported("mouse_click")
mouse_scroll = _unsupported("mouse_scroll")
type_text = _unsupported("type_text")
press_key = _unsupported("press_key")
clipboard_read = _unsupported("clipboard_read")
clipboard_write = _unsupported("clipboard_write")
send_notification = _unsupported("send_notification")
list_windows = _unsupported("list_windows")
focus_window = _unsupported("focus_window")
get_virtual_screen_bounds = _unsupported("get_virtual_screen_bounds")
