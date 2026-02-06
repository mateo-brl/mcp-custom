"""Windows API helpers - wrappers ctypes pour user32.dll et kernel32.dll."""

import ctypes
from ctypes import wintypes

# References DLL
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


# =============================================================================
# STRUCTURES
# =============================================================================

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


# =============================================================================
# CONSTANTES
# =============================================================================

# Types d'input
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

# Evenements souris
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

# Evenements clavier
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

# Codes de touches virtuelles
VK_CODES = {
    "enter": 0x0D, "return": 0x0D,
    "tab": 0x09,
    "escape": 0x1B, "esc": 0x1B,
    "backspace": 0x08,
    "delete": 0x2E,
    "space": 0x20,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "home": 0x24, "end": 0x23,
    "pageup": 0x21, "pagedown": 0x22,
    "ctrl": 0x11, "alt": 0x12, "shift": 0x10,
    "win": 0x5B,
    "insert": 0x2D,
    "printscreen": 0x2C,
    "numlock": 0x90, "capslock": 0x14, "scrolllock": 0x91,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "a": 0x41, "b": 0x42, "c": 0x43, "d": 0x44, "e": 0x45,
    "f": 0x46, "g": 0x47, "h": 0x48, "i": 0x49, "j": 0x4A,
    "k": 0x4B, "l": 0x4C, "m": 0x4D, "n": 0x4E, "o": 0x4F,
    "p": 0x50, "q": 0x51, "r": 0x52, "s": 0x53, "t": 0x54,
    "u": 0x55, "v": 0x56, "w": 0x57, "x": 0x58, "y": 0x59, "z": 0x5A,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
}

# Metriques ecran
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77


# =============================================================================
# FONCTIONS HELPER
# =============================================================================

def get_cursor_pos():
    """Recupere la position de la souris."""
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def set_cursor_pos(x, y):
    """Deplace la souris."""
    user32.SetCursorPos(int(x), int(y))


def mouse_click(x, y, button="left"):
    """Effectue un clic a une position donnee."""
    set_cursor_pos(x, y)

    buttons = {
        "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
        "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
        "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
    }
    down, up = buttons.get(button, buttons["left"])
    user32.mouse_event(down, 0, 0, 0, 0)
    user32.mouse_event(up, 0, 0, 0, 0)


def mouse_scroll(clicks):
    """Effectue un scroll."""
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, clicks * WHEEL_DELTA, 0)


def send_input(*inputs):
    """Envoie une ou plusieurs structures INPUT via SendInput."""
    n = len(inputs)
    arr = (INPUT * n)(*inputs)
    user32.SendInput(n, arr, ctypes.sizeof(INPUT))


def make_key_input(vk=0, scan=0, flags=0):
    """Cree une structure INPUT pour le clavier."""
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = scan
    inp.union.ki.dwFlags = flags
    return inp


def make_unicode_input(char_code, key_up=False):
    """Cree une structure INPUT Unicode pour un caractere."""
    flags = KEYEVENTF_UNICODE
    if key_up:
        flags |= KEYEVENTF_KEYUP
    return make_key_input(vk=0, scan=char_code, flags=flags)


def get_virtual_screen_bounds():
    """Retourne les limites de l'ecran virtuel (multi-moniteurs)."""
    x = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    y = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    w = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    h = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    return x, y, w, h
