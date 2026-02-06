"""Backend Linux - pynput, pyperclip, notifypy, wmctrl."""

import shutil
import subprocess
import time


# =============================================================================
# SOURIS
# =============================================================================

def _get_mouse():
    """Lazy init du controleur souris pynput."""
    from pynput.mouse import Controller
    return Controller()


def get_cursor_pos():
    """Recupere la position de la souris."""
    m = _get_mouse()
    return m.position


def set_cursor_pos(x, y):
    """Deplace la souris."""
    m = _get_mouse()
    m.position = (int(x), int(y))


def mouse_click(x, y, button="left"):
    """Effectue un clic a une position donnee."""
    from pynput.mouse import Button
    m = _get_mouse()
    m.position = (int(x), int(y))
    btn_map = {"left": Button.left, "right": Button.right, "middle": Button.middle}
    m.click(btn_map.get(button, Button.left))


def mouse_scroll(clicks):
    """Effectue un scroll."""
    m = _get_mouse()
    m.scroll(0, clicks)


# =============================================================================
# CLAVIER
# =============================================================================

def _get_keyboard():
    """Lazy init du controleur clavier pynput."""
    from pynput.keyboard import Controller
    return Controller()


KEY_MAP = None


def _get_key_map():
    """Lazy init du mapping de touches pynput."""
    global KEY_MAP
    if KEY_MAP is not None:
        return KEY_MAP

    from pynput.keyboard import Key
    KEY_MAP = {
        "enter": Key.enter, "return": Key.enter,
        "tab": Key.tab,
        "escape": Key.esc, "esc": Key.esc,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "space": Key.space,
        "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
        "home": Key.home, "end": Key.end,
        "pageup": Key.page_up, "pagedown": Key.page_down,
        "ctrl": Key.ctrl, "alt": Key.alt, "shift": Key.shift,
        "insert": Key.insert,
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
    }
    return KEY_MAP


def type_text(text, interval=0.05):
    """Tape du texte caractere par caractere."""
    kb = _get_keyboard()
    for char in text:
        kb.type(char)
        time.sleep(interval)


def press_key(key_name):
    """Appuie sur une touche ou combinaison (ex: 'ctrl+c')."""
    from pynput.keyboard import KeyCode
    kb = _get_keyboard()
    key_map = _get_key_map()

    if "+" in key_name:
        keys = [k.strip().lower() for k in key_name.split("+")]
        resolved = []
        for key in keys:
            if key in key_map:
                resolved.append(key_map[key])
            elif len(key) == 1:
                resolved.append(KeyCode.from_char(key))
            else:
                raise ValueError(f"Touche inconnue: {key}")
        # Appuyer dans l'ordre, relacher en sens inverse
        for k in resolved:
            kb.press(k)
        for k in reversed(resolved):
            kb.release(k)
    else:
        key_lower = key_name.lower()
        if key_lower in key_map:
            kb.press(key_map[key_lower])
            kb.release(key_map[key_lower])
        elif len(key_lower) == 1:
            kb.press(KeyCode.from_char(key_lower))
            kb.release(KeyCode.from_char(key_lower))
        else:
            raise ValueError(f"Touche inconnue: {key_name}")


# =============================================================================
# PRESSE-PAPIER
# =============================================================================

def clipboard_read():
    """Lit le texte du presse-papier via pyperclip."""
    import pyperclip
    return pyperclip.paste()


def clipboard_write(text):
    """Ecrit du texte dans le presse-papier via pyperclip."""
    import pyperclip
    pyperclip.copy(text)


# =============================================================================
# NOTIFICATIONS
# =============================================================================

def send_notification(title, message, duration="short"):
    """Envoie une notification desktop via notifypy."""
    from notifypy import Notify
    n = Notify()
    n.title = title
    n.message = message
    n.send()


# =============================================================================
# FENETRES
# =============================================================================

def list_windows():
    """Liste les fenetres ouvertes via wmctrl."""
    wmctrl_path = shutil.which("wmctrl")
    if not wmctrl_path:
        raise RuntimeError(
            "wmctrl non installe. Installez avec: sudo apt install wmctrl"
        )

    result = subprocess.run(
        ["wmctrl", "-l", "-G"], capture_output=True, text=True, timeout=5
    )
    windows = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split(None, 8)
        if len(parts) >= 9:
            windows.append({
                "titre": parts[8],
                "position": f"({parts[3]}, {parts[4]})",
                "taille": f"{parts[5]}x{parts[6]}",
                "visible": True,
                "minimisee": False,
                "active": False,
            })
    return windows


def focus_window(title):
    """Active une fenetre par titre via wmctrl."""
    wmctrl_path = shutil.which("wmctrl")
    if not wmctrl_path:
        raise RuntimeError(
            "wmctrl non installe. Installez avec: sudo apt install wmctrl"
        )

    result = subprocess.run(
        ["wmctrl", "-a", title], capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        raise RuntimeError(f"Aucune fenetre trouvee avec: '{title}'")
    return title


# =============================================================================
# ECRAN
# =============================================================================

def get_virtual_screen_bounds():
    """Retourne les limites de l'ecran virtuel."""
    try:
        result = subprocess.run(
            ["xdpyinfo"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "dimensions:" in line:
                dims = line.split()[1]
                w, h = dims.split("x")
                return 0, 0, int(w), int(h)
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # Fallback: essayer xrandr
    try:
        result = subprocess.run(
            ["xrandr", "--current"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if " connected " in line and "x" in line:
                import re
                match = re.search(r"(\d+)x(\d+)", line)
                if match:
                    return 0, 0, int(match.group(1)), int(match.group(2))
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # Dernier recours
    return 0, 0, 1920, 1080
