"""Outils MCP pour la surveillance systeme et gestion des processus."""

import json
import platform
import sys

# Processus critiques proteges contre la terminaison
if sys.platform == "win32":
    PROTECTED_PROCESSES = {
        "csrss.exe", "wininit.exe", "winlogon.exe", "services.exe",
        "lsass.exe", "smss.exe", "svchost.exe", "explorer.exe",
        "dwm.exe", "system", "system idle process", "registry",
        "fontdrvhost.exe", "sihost.exe", "taskhostw.exe",
    }
else:
    PROTECTED_PROCESSES = {
        "init", "systemd", "kthreadd", "ksoftirqd", "kworker",
        "rcu_sched", "migration", "watchdog", "sshd", "cron",
        "dbus-daemon", "networkmanager", "journald", "udevd",
        "xorg", "gdm", "lightdm", "pulseaudio", "pipewire",
    }


def liste_processus(tri: str = "memory") -> str:
    """
    Liste les processus en cours d'execution.

    Args:
        tri: Critere de tri - "memory", "cpu", ou "name" (defaut: "memory")

    Returns:
        Les 50 premiers processus tries par le critere choisi.
    """
    try:
        import psutil
    except ImportError:
        return "Erreur: psutil non installe. pip install psutil"

    try:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                info = proc.info
                mem = info["memory_info"]
                processes.append({
                    "pid": info["pid"],
                    "nom": info["name"],
                    "cpu_pourcent": info["cpu_percent"] or 0.0,
                    "memoire_mo": round(mem.rss / (1024 * 1024), 1) if mem else 0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if tri == "cpu":
            processes.sort(key=lambda p: p["cpu_pourcent"], reverse=True)
        elif tri == "name":
            processes.sort(key=lambda p: p["nom"].lower())
        else:
            processes.sort(key=lambda p: p["memoire_mo"], reverse=True)

        return json.dumps({
            "nombre_total": len(processes),
            "tri": tri,
            "processus": processes[:50],
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Erreur: {str(e)}"


def info_systeme() -> str:
    """
    Retourne les informations systeme (CPU, RAM, disque, OS).

    Returns:
        Les informations systeme detaillees.
    """
    try:
        import psutil
    except ImportError:
        return "Erreur: psutil non installe. pip install psutil"

    try:
        mem = psutil.virtual_memory()

        disques = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disques.append({
                    "lecteur": part.device,
                    "point_montage": part.mountpoint,
                    "systeme_fichiers": part.fstype,
                    "total_go": round(usage.total / (1024**3), 1),
                    "utilise_go": round(usage.used / (1024**3), 1),
                    "libre_go": round(usage.free / (1024**3), 1),
                    "utilisation_pourcent": usage.percent,
                })
            except (PermissionError, OSError):
                continue

        result = {
            "os": {
                "systeme": platform.system(),
                "version": platform.version(),
                "architecture": platform.machine(),
                "processeur": platform.processor(),
                "nom_machine": platform.node(),
            },
            "cpu": {
                "coeurs_physiques": psutil.cpu_count(logical=False),
                "coeurs_logiques": psutil.cpu_count(logical=True),
                "utilisation_pourcent": psutil.cpu_percent(interval=1),
            },
            "memoire": {
                "total_go": round(mem.total / (1024**3), 1),
                "utilise_go": round(mem.used / (1024**3), 1),
                "disponible_go": round(mem.available / (1024**3), 1),
                "utilisation_pourcent": mem.percent,
            },
            "disques": disques,
        }

        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Erreur: {str(e)}"


def tuer_processus(pid_ou_nom: str) -> str:
    """
    Termine un processus par PID ou nom.

    Args:
        pid_ou_nom: PID numerique ou nom du processus (ex: "1234" ou "notepad.exe")

    Returns:
        Confirmation ou erreur.
    """
    try:
        import psutil
    except ImportError:
        return "Erreur: psutil non installe. pip install psutil"

    try:
        # Determiner si c'est un PID ou un nom
        if pid_ou_nom.isdigit():
            pid = int(pid_ou_nom)
            try:
                proc = psutil.Process(pid)
            except psutil.NoSuchProcess:
                return f"Erreur: aucun processus avec le PID {pid}"

            name = proc.name().lower()
            if name in PROTECTED_PROCESSES:
                return f"Refuse: '{name}' (PID {pid}) est un processus systeme protege"

            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()

            return f"Processus termine: '{proc.name()}' (PID {pid})"
        else:
            nom = pid_ou_nom.lower()
            if nom in PROTECTED_PROCESSES:
                return f"Refuse: '{pid_ou_nom}' est un processus systeme protege"

            killed = []
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.info["name"].lower() == nom:
                        proc.terminate()
                        killed.append(proc.info["pid"])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not killed:
                return f"Aucun processus trouve avec le nom '{pid_ou_nom}'"
            return f"Processus termines: '{pid_ou_nom}' (PIDs: {killed})"
    except psutil.AccessDenied:
        return f"Erreur: acces refuse pour terminer '{pid_ou_nom}' (droits admin requis ?)"
    except Exception as e:
        return f"Erreur: {str(e)}"


def register_tools(mcp):
    """Enregistre les outils systeme sur l'instance MCP."""
    mcp.add_tool(liste_processus)
    mcp.add_tool(info_systeme)
    mcp.add_tool(tuer_processus)
