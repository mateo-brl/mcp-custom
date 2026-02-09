"""Tests pour le module execution."""

import json
import sys

from mon_mcp.tools.execution import (
    executer_commande,
    executer_python,
    verifier_commande,
    lister_environnement,
)


def test_executer_commande_echo():
    """Test commande basique echo."""
    if sys.platform == "win32":
        result = json.loads(executer_commande("echo hello"))
    else:
        result = json.loads(executer_commande("echo hello"))
    assert result["code_retour"] == 0
    assert "hello" in result["stdout"]
    assert result["timeout"] is False


def test_executer_commande_bloquee():
    """Test que les commandes dangereuses sont bloquees."""
    result = json.loads(executer_commande("rm -rf /"))
    assert "erreur" in result
    assert "bloquee" in result["erreur"].lower() or "securite" in result["erreur"].lower()


def test_executer_commande_repertoire_inexistant():
    """Test commande dans un repertoire inexistant."""
    result = json.loads(executer_commande("echo test", repertoire="/chemin/inexistant/xyz"))
    assert "erreur" in result


def test_executer_python_basique():
    """Test execution Python simple."""
    result = json.loads(executer_python("print('hello world')"))
    assert result["success"] is True
    assert "hello world" in result["stdout"]


def test_executer_python_erreur_syntaxe():
    """Test execution Python avec erreur de syntaxe."""
    result = json.loads(executer_python("def foo("))
    assert result["success"] is False
    assert "SyntaxError" in result["exception"]


def test_executer_python_exception():
    """Test execution Python avec exception runtime."""
    result = json.loads(executer_python("raise ValueError('test error')"))
    assert result["success"] is False


def test_verifier_commande_python():
    """Test que python est trouve."""
    result = json.loads(verifier_commande("python"))
    assert result["existe"] is True
    assert result["chemin"] is not None


def test_verifier_commande_inexistante():
    """Test commande qui n'existe pas."""
    result = json.loads(verifier_commande("commande_totalement_inexistante_xyz"))
    assert result["existe"] is False


def test_lister_environnement():
    """Test listing des variables d'environnement."""
    result = json.loads(lister_environnement())
    assert "variables" in result
    assert result["total"] > 0
    assert "PATH" in result["variables"]
