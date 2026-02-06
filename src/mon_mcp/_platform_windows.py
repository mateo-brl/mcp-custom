"""Backend Windows - wrappers ctypes pour user32.dll et kernel32.dll."""

import ctypes
import json
import time
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

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

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

SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77

# Clipboard
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


# =============================================================================
# FONCTIONS BAS NIVEAU
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


# =============================================================================
# FONCTIONS HAUT NIVEAU (API unifiee)
# =============================================================================

def type_text(text, interval=0.05):
    """Tape du texte caractere par caractere via SendInput UNICODE."""
    for char in text:
        code = ord(char)
        down = make_unicode_input(code, key_up=False)
        up = make_unicode_input(code, key_up=True)
        send_input(down, up)
        time.sleep(interval)


def press_key(key_name):
    """Appuie sur une touche ou combinaison (ex: 'ctrl+c')."""
    if "+" in key_name:
        keys = [k.strip().lower() for k in key_name.split("+")]
        for key in keys:
            vk = VK_CODES.get(key)
            if vk:
                send_input(make_key_input(vk=vk))
        for key in reversed(keys):
            vk = VK_CODES.get(key)
            if vk:
                send_input(make_key_input(vk=vk, flags=KEYEVENTF_KEYUP))
    else:
        vk = VK_CODES.get(key_name.lower())
        if vk:
            send_input(make_key_input(vk=vk))
            send_input(make_key_input(vk=vk, flags=KEYEVENTF_KEYUP))
        else:
            raise ValueError(f"Touche inconnue: {key_name}")


def clipboard_read():
    """Lit le texte du presse-papier Windows."""
    if not user32.OpenClipboard(0):
        raise RuntimeError("Impossible d'ouvrir le presse-papier")
    try:
        if not user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
            return ""
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return ""
        kernel32.GlobalLock.restype = ctypes.c_wchar_p
        text = kernel32.GlobalLock(handle)
        result = str(text) if text else ""
        kernel32.GlobalUnlock(handle)
        return result
    finally:
        user32.CloseClipboard()


def clipboard_write(text):
    """Ecrit du texte dans le presse-papier Windows."""
    if not user32.OpenClipboard(0):
        raise RuntimeError("Impossible d'ouvrir le presse-papier")
    try:
        user32.EmptyClipboard()
        encoded = text.encode("utf-16-le") + b"\x00\x00"
        h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
        if not h_mem:
            raise RuntimeError("Allocation memoire echouee")
        kernel32.GlobalLock.restype = ctypes.c_void_p
        ptr = kernel32.GlobalLock(h_mem)
        ctypes.memmove(ptr, encoded, len(encoded))
        kernel32.GlobalUnlock(h_mem)
        user32.SetClipboardData(CF_UNICODETEXT, h_mem)
    finally:
        user32.CloseClipboard()


def send_notification(title, message, duration="short"):
    """Envoie une notification toast Windows via winotify."""
    from winotify import Notification, audio
    toast = Notification(
        app_id="MCP Custom",
        title=title,
        msg=message,
        duration=duration,
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()


def list_windows():
    """Liste les fenetres ouvertes via pygetwindow."""
    import pygetwindow as gw
    windows = gw.getAllWindows()
    result = []
    for win in windows:
        if win.title:
            result.append({
                "titre": win.title,
                "position": f"({win.left}, {win.top})",
                "taille": f"{win.width}x{win.height}",
                "visible": win.visible,
                "minimisee": win.isMinimized,
                "active": win.isActive,
            })
    return result


def focus_window(title):
    """Active une fenetre par titre (partiel) via pygetwindow."""
    import pygetwindow as gw
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        raise RuntimeError(f"Aucune fenetre trouvee avec: '{title}'")
    win = windows[0]
    if win.isMinimized:
        win.restore()
    win.activate()
    return win.title
