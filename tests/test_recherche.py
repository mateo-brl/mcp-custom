"""Tests pour les outils de recherche de fichiers."""

import json

from mon_mcp.tools.recherche import rechercher_fichiers


def test_recherche_par_nom(tmp_path):
    """Test recherche par pattern de nom."""
    (tmp_path / "rapport.txt").write_text("contenu")
    (tmp_path / "rapport.csv").write_text("data")
    (tmp_path / "notes.txt").write_text("notes")

    result = rechercher_fichiers(str(tmp_path), motif="rapport*")
    data = json.loads(result)
    assert data["nombre_resultats"] == 2


def test_recherche_par_contenu(tmp_path):
    """Test recherche par contenu."""
    (tmp_path / "a.txt").write_text("Bonjour le monde")
    (tmp_path / "b.txt").write_text("Hello world")
    (tmp_path / "c.txt").write_text("Bonjour Claude")

    result = rechercher_fichiers(str(tmp_path), contenu="Bonjour")
    data = json.loads(result)
    assert data["nombre_resultats"] == 2


def test_recherche_par_extension(tmp_path):
    """Test recherche filtree par extension."""
    (tmp_path / "code.py").write_text("print()")
    (tmp_path / "doc.txt").write_text("texte")
    (tmp_path / "style.css").write_text("body{}")

    result = rechercher_fichiers(str(tmp_path), extensions=".py,.css")
    data = json.loads(result)
    assert data["nombre_resultats"] == 2


def test_recherche_max_resultats(tmp_path):
    """Test limite de resultats."""
    for i in range(10):
        (tmp_path / f"file{i}.txt").write_text(f"contenu {i}")

    result = rechercher_fichiers(str(tmp_path), max_resultats=3)
    data = json.loads(result)
    assert data["nombre_resultats"] == 3
    assert data["limite_atteinte"] is True


def test_recherche_dossier_inexistant():
    """Test avec un dossier qui n'existe pas."""
    result = rechercher_fichiers("C:\\dossier_inexistant_xyz")
    assert "n'existe pas" in result
