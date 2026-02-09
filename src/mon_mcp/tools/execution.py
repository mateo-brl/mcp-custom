"""
Module d'execution de code et commandes.

Outils: executer_commande, executer_python, executer_script,
        verifier_commande, lister_environnement
"""

import json
import os
import shutil
import subprocess
import sys

# Limite de sortie stdout/stderr (100 KB)
MAX_OUTPUT_SIZE = 100_000

# Patterns de commandes bloquees (dangereuses)
BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "rm -rf ~",
    "del /f /s /q c:\\",
    "format c:",
    "format d:",
    "dd if=",
    ":(){ :|:& };:",
    "mkfs",
    "shutdown",
    "reboot",
    "halt",
    "init 0",
    "init 6",
    "> /dev/sda",
    "mv /* /dev/null",
    "chmod -r 000 /",
    "chown -r",
]

# Patterns de variables d'environnement sensibles
SENSITIVE_ENV_PATTERNS = [
    "password", "passwd", "secret", "token", "key", "api_key",
    "apikey", "credential", "auth", "private", "jwt", "session",
    "cookie", "access_key", "secret_key",
]


def _is_blocked(commande: str) -> bool:
    """Verifie si une commande est dans la liste noire."""
    cmd_lower = commande.lower().strip()
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd_lower:
            return True
    return False


def _truncate_output(text: str) -> tuple[str, bool]:
    """Tronque la sortie si elle depasse la limite."""
    if len(text) > MAX_OUTPUT_SIZE:
        return text[:MAX_OUTPUT_SIZE] + "\n... [TRONQUE]", True
    return text, False


def executer_commande(commande: str, repertoire: str = ".", timeout: int = 30) -> str:
    """
    Execute une commande shell et capture la sortie.

    Args:
        commande: La commande a executer (ex: "ls -la", "dir", "git status")
        repertoire: Repertoire de travail (defaut: repertoire courant)
        timeout: Timeout en secondes (defaut: 30, max: 300)

    Returns:
        JSON avec code_retour, stdout, stderr, duree, timeout, tronque.
    """
    if _is_blocked(commande):
        return json.dumps({"erreur": f"Commande bloquee pour raison de securite: {commande}"})

    timeout = min(max(1, timeout), 300)
    repertoire = os.path.abspath(repertoire)

    if not os.path.isdir(repertoire):
        return json.dumps({"erreur": f"Repertoire inexistant: {repertoire}"})

    try:
        # Sous Windows, on utilise shell=True pour les commandes internes (dir, type, etc.)
        use_shell = sys.platform == "win32"

        import time
        start = time.time()

        result = subprocess.run(
            commande if use_shell else commande.split(),
            shell=use_shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=repertoire,
        )

        duree = round(time.time() - start, 3)
        stdout, stdout_tronque = _truncate_output(result.stdout)
        stderr, stderr_tronque = _truncate_output(result.stderr)

        return json.dumps({
            "code_retour": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "duree_secondes": duree,
            "timeout": False,
            "tronque": stdout_tronque or stderr_tronque,
        }, ensure_ascii=False)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "code_retour": -1,
            "stdout": "",
            "stderr": f"Timeout apres {timeout} secondes.",
            "duree_secondes": timeout,
            "timeout": True,
            "tronque": False,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"erreur": str(e)}, ensure_ascii=False)


def executer_python(code: str, repertoire: str = ".", timeout: int = 30) -> str:
    """
    Execute du code Python dans un subprocess isole.

    Args:
        code: Le code Python a executer
        repertoire: Repertoire de travail (defaut: repertoire courant)
        timeout: Timeout en secondes (defaut: 30, max: 300)

    Returns:
        JSON avec success, stdout, stderr, duree, exception.
    """
    timeout = min(max(1, timeout), 300)
    repertoire = os.path.abspath(repertoire)

    if not os.path.isdir(repertoire):
        return json.dumps({"erreur": f"Repertoire inexistant: {repertoire}"})

    # Verification syntaxe avant execution
    try:
        compile(code, "<code>", "exec")
    except SyntaxError as e:
        return json.dumps({
            "success": False,
            "stdout": "",
            "stderr": "",
            "duree_secondes": 0,
            "exception": f"SyntaxError: {e.msg} (ligne {e.lineno})",
        }, ensure_ascii=False)

    try:
        import time
        start = time.time()

        python_exec = sys.executable or "python"
        result = subprocess.run(
            [python_exec, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=repertoire,
        )

        duree = round(time.time() - start, 3)
        stdout, _ = _truncate_output(result.stdout)
        stderr, _ = _truncate_output(result.stderr)

        return json.dumps({
            "success": result.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "duree_secondes": duree,
            "exception": None if result.returncode == 0 else stderr.strip().split("\n")[-1] if stderr else None,
        }, ensure_ascii=False)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "success": False,
            "stdout": "",
            "stderr": f"Timeout apres {timeout} secondes.",
            "duree_secondes": timeout,
            "exception": "TimeoutError",
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"erreur": str(e)}, ensure_ascii=False)


def executer_script(chemin: str, args: str = "[]", timeout: int = 60) -> str:
    """
    Execute un fichier script (.py, .sh, .bat, .ps1).

    Args:
        chemin: Chemin du script a executer
        args: Arguments en JSON (liste de strings, ex: '["arg1", "arg2"]')
        timeout: Timeout en secondes (defaut: 60, max: 300)

    Returns:
        JSON avec code_retour, stdout, stderr, duree.
    """
    chemin = os.path.abspath(chemin)

    if not os.path.isfile(chemin):
        return json.dumps({"erreur": f"Script introuvable: {chemin}"})

    ext = os.path.splitext(chemin)[1].lower()
    extensions_valides = {".py", ".sh", ".bat", ".cmd", ".ps1"}
    if ext not in extensions_valides:
        return json.dumps({"erreur": f"Extension non supportee: {ext}. Valides: {', '.join(extensions_valides)}"})

    try:
        arguments = json.loads(args) if isinstance(args, str) else args
        if not isinstance(arguments, list):
            arguments = []
    except json.JSONDecodeError:
        arguments = []

    timeout = min(max(1, timeout), 300)

    # Construire la commande selon le type de script
    if ext == ".py":
        cmd = [sys.executable or "python", chemin] + [str(a) for a in arguments]
    elif ext in (".sh",):
        cmd = ["bash", chemin] + [str(a) for a in arguments]
    elif ext in (".bat", ".cmd"):
        cmd = ["cmd", "/c", chemin] + [str(a) for a in arguments]
    elif ext == ".ps1":
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", chemin] + [str(a) for a in arguments]
    else:
        cmd = [chemin] + [str(a) for a in arguments]

    try:
        import time
        start = time.time()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(chemin),
        )

        duree = round(time.time() - start, 3)
        stdout, stdout_tronque = _truncate_output(result.stdout)
        stderr, stderr_tronque = _truncate_output(result.stderr)

        return json.dumps({
            "script": chemin,
            "code_retour": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "duree_secondes": duree,
            "timeout": False,
            "tronque": stdout_tronque or stderr_tronque,
        }, ensure_ascii=False)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "script": chemin,
            "code_retour": -1,
            "stdout": "",
            "stderr": f"Timeout apres {timeout} secondes.",
            "duree_secondes": timeout,
            "timeout": True,
            "tronque": False,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"erreur": str(e)}, ensure_ascii=False)


def verifier_commande(commande: str) -> str:
    """
    Verifie si un executable existe sur le systeme.

    Args:
        commande: Nom de l'executable a verifier (ex: "python", "git", "node")

    Returns:
        JSON avec existe, chemin, et version si disponible.
    """
    chemin = shutil.which(commande)

    if not chemin:
        return json.dumps({
            "commande": commande,
            "existe": False,
            "chemin": None,
            "version": None,
        }, ensure_ascii=False)

    # Essayer d'obtenir la version
    version = None
    for flag in ["--version", "-V", "version"]:
        try:
            result = subprocess.run(
                [chemin, flag],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = (result.stdout + result.stderr).strip()
            if output and len(output) < 200:
                version = output.split("\n")[0]
                break
        except Exception:
            continue

    return json.dumps({
        "commande": commande,
        "existe": True,
        "chemin": chemin,
        "version": version,
    }, ensure_ascii=False)


def lister_environnement() -> str:
    """
    Liste les variables d'environnement (filtre les secrets).

    Returns:
        JSON avec les variables d'environnement (sensibles masquees).
    """
    env_vars = {}
    for key, value in sorted(os.environ.items()):
        key_lower = key.lower()
        is_sensitive = any(pattern in key_lower for pattern in SENSITIVE_ENV_PATTERNS)
        env_vars[key] = "***MASQUE***" if is_sensitive else value

    return json.dumps({
        "variables": env_vars,
        "total": len(env_vars),
        "masquees": sum(1 for v in env_vars.values() if v == "***MASQUE***"),
        "plateforme": sys.platform,
    }, ensure_ascii=False)


def register_tools(mcp):
    mcp.add_tool(executer_commande)
    mcp.add_tool(executer_python)
    mcp.add_tool(executer_script)
    mcp.add_tool(verifier_commande)
    mcp.add_tool(lister_environnement)
