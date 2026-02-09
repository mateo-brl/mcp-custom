"""Tests pour le module workspace."""

import json
import os
import tempfile

from mon_mcp.tools.workspace import (
    definir_workspace,
    obtenir_workspace,
    lister_workspace,
    nettoyer_workspace,
    archiver_workspace,
)


def test_definir_workspace():
    """Test creation d'un workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ws_path = os.path.join(tmpdir, "test_ws")
        result = json.loads(definir_workspace(ws_path))
        assert result["workspace"] == os.path.abspath(ws_path)
        assert result["cree"] is True
        assert os.path.isdir(ws_path)


def test_definir_workspace_chemin_protege():
    """Test que les chemins systeme sont refuses."""
    if os.name == "nt":
        result = json.loads(definir_workspace("C:\\Windows"))
    else:
        result = json.loads(definir_workspace("/"))
    assert "erreur" in result


def test_obtenir_workspace():
    """Test obtention info du workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        definir_workspace(tmpdir)
        # Creer un fichier test
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("hello")
        result = json.loads(obtenir_workspace())
        assert result["actif"] is True
        assert result["fichiers"] >= 1


def test_lister_workspace():
    """Test listing des fichiers du workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        definir_workspace(tmpdir)
        # Creer des fichiers
        for name in ["a.txt", "b.py", "c.txt"]:
            with open(os.path.join(tmpdir, name), "w") as f:
                f.write("test")
        result = json.loads(lister_workspace("*.txt"))
        assert result["total"] == 2


def test_nettoyer_workspace_dry_run():
    """Test nettoyage en mode dry-run."""
    with tempfile.TemporaryDirectory() as tmpdir:
        definir_workspace(tmpdir)
        # Creer des fichiers tmp
        with open(os.path.join(tmpdir, "test.tmp"), "w") as f:
            f.write("temp")
        with open(os.path.join(tmpdir, "keep.txt"), "w") as f:
            f.write("keep")
        result = json.loads(nettoyer_workspace(confirmer=False))
        assert result["action"] == "dry-run"
        assert result["total"] >= 1
        # Le fichier tmp existe toujours en dry-run
        assert os.path.exists(os.path.join(tmpdir, "test.tmp"))


def test_archiver_workspace():
    """Test archivage du workspace en zip."""
    with tempfile.TemporaryDirectory() as tmpdir:
        definir_workspace(tmpdir)
        with open(os.path.join(tmpdir, "doc.txt"), "w") as f:
            f.write("contenu")
        zip_path = os.path.join(tmpdir, "archive.zip")
        result = json.loads(archiver_workspace(zip_path))
        assert result["fichiers_archives"] >= 1
        assert os.path.exists(zip_path)
